# clip_recorder_ring.py
import time
import threading
import subprocess
from collections import deque
from pathlib import Path

from picamera2.encoders import H264Encoder
from picamera2.outputs import Output  # základní base class pro vlastní output

CLIP_DIR = Path("/mnt/p3/clips")
CLIP_DIR.mkdir(parents=True, exist_ok=True)


class RingBufferOutput(Output):
    """
    Ring buffer pro H.264 stream v RAM, limitovaný:
      - časem (posledních max_seconds podle timestampu),
      - volitelně i počtem bajtů (max_bytes) jako pojistka.

    Uvnitř drží deque((ts_sec, data_bytes)).
    """

    def __init__(self, max_seconds: float, max_bytes: int | None = None):
        super().__init__()
        self.max_seconds = float(max_seconds)
        self.max_bytes = max_bytes
        self._chunks = deque()     # prvky: (ts_sec: float, data: bytes)
        self._total_bytes = 0
        self._latest_ts = None     # poslední známý timestamp v sekundách
        self._lock = threading.Lock()

    def _convert_timestamp_to_seconds(self, timestamp):
        """
        Picamera2 timestamp bývá v µs nebo ns.
        Uděláme heuristiku:
          - >1e12 -> předpokládáme ns (1e9 ns = 1 s),
          - jinak předpokládáme µs (1e6 µs = 1 s).
        """
        if timestamp is None:
            return None
        try:
            t = float(timestamp)
        except (TypeError, ValueError):
            return None

        if t > 1e12:
            # předpoklad: nanosekundy
            return t / 1e9
        else:
            # předpoklad: mikrosekundy
            return t / 1e6

    def outputframe(self, frame, keyframe=True, timestamp=None,
                    packet=None, audio=None):
        """
        Volá Picamera2 encoder pro každý kus H.264.

        Nás zajímá:
          - frame -> H.264 byty,
          - timestamp -> reálný čas (převedeme na sekundy).

        Uložíme (ts_sec, data) do deque a:
          - ořízneme staré chunk podle času (max_seconds),
          - případně ještě podle max_bytes.
        """
        data = bytes(frame)
        size = len(data)

        ts_sec = self._convert_timestamp_to_seconds(timestamp)
        now_monotonic = time.monotonic()

        # fallback, kdyby timestamp nebyl k dispozici
        if ts_sec is None:
            if self._latest_ts is None:
                ts_sec = now_monotonic
            else:
                # pokud nemáme nový timestamp, použijeme poslední známý
                ts_sec = self._latest_ts

        with self._lock:
            self._chunks.append((ts_sec, data))
            self._total_bytes += size
            self._latest_ts = ts_sec

            # 1) ořez podle času: necháme jen chunk s ts >= (latest_ts - max_seconds)
            if self._latest_ts is not None and self.max_seconds is not None:
                cutoff = self._latest_ts - self.max_seconds
                while self._chunks and self._chunks[0][0] < cutoff:
                    old_ts, old_data = self._chunks.popleft()
                    self._total_bytes -= len(old_data)

            # 2) pojistka podle max_bytes
            if self.max_bytes is not None:
                while self._total_bytes > self.max_bytes and self._chunks:
                    old_ts, old_data = self._chunks.popleft()
                    self._total_bytes -= len(old_data)

    def snapshot(self):
        """
        Vrátí kopii aktuálního obsahu bufferu:

          chunks: list[bytes]          – H.264 data
          total_bytes: int             – celková velikost v bajtech
          duration_seconds: float      – délka podle timestampů (poslední - první)

        Ring buffer uvnitř běží dál.
        """
        with self._lock:
            chunks_data = [data for (_, data) in self._chunks]
            total_bytes = self._total_bytes

            if len(self._chunks) >= 2:
                first_ts = self._chunks[0][0]
                last_ts = self._chunks[-1][0]
                duration_seconds = max(0.0, last_ts - first_ts)
            else:
                duration_seconds = 0.0

            return chunks_data, total_bytes, duration_seconds

    def clear(self):
        """Vymaže obsah ring bufferu (pokud bys chtěl začít od nuly)."""
        with self._lock:
            self._chunks.clear()
            self._total_bytes = 0
            self._latest_ts = None


class ClipRecorderRing:
    """
    Recorder, který:

    - běží kontinuálně: H.264 encoder sype data do RingBufferOutput v RAM
    - RingBufferOutput drží posledních `seconds` podle timestampu
      (a navíc má pojistný limit na velikost v bajtech),
    - na request_clip() v SAMOSTATNÉM VLÁKNĚ:
        1) vezme snapshot bufferu (kopii stavu),
        2) z té kopie udělá dočasný .h264,
        3) přes ffmpeg z něj vytvoří .mp4,
        4) po úspěchu .h264 smaže.

    Navíc:
    - loguje chunks, total_bytes, odhad délky z bajtů (~seconds_bytes),
      i reálnou délku z timestampů (seconds_ts),
    - vytváří .meta.txt s informacemi,
    - do last_clip_info uloží info o posledním klipu.
    """

    def __init__(self,
                 picam2,
                 seconds=10,
                 bitrate=5_000_000,
                 fps=20):
        self.picam2 = picam2
        self.seconds = seconds
        self.bitrate = bitrate
        self.fps = fps

        # Odhad potřebných bajtů: bitrate [bit/s] -> B/s * seconds
        # používáme to jako max_bytes pojistku, hlavní limit je teď časový.
        bytes_per_second = int(self.bitrate / 8)
        max_bytes = bytes_per_second * self.seconds

        # Ring buffer limitovaný časem + pojistným limitem v bajtech
        self.ring = RingBufferOutput(
            max_seconds=self.seconds,
            max_bytes=max_bytes,
        )

        self.encoder = H264Encoder(
            bitrate=self.bitrate,
            framerate=self.fps,
            enable_sps_framerate=True,
        )

        self._recording = False
        self._saving = False
        self._lock = threading.Lock()

        # informace o posledním uloženém klipu
        self.last_clip_info = None  # dict nebo None

    def start(self):
        """Spustí kontinuální kódování H.264 do RAM ring bufferu."""
        if not self._recording:
            print("[ClipRecorderRing] start_recording -> ring buffer")
            self.picam2.start_recording(self.encoder, self.ring)
            self._recording = True

    def request_clip(self):
        """
        Spustí uložení posledních N sekund v samostatném vlákně.

        - Neblokuje volající thread.
        - Pokud už se jeden klip ukládá, další požadavek ignoruje.
        """
        with self._lock:
            if not self._recording:
                print("[ClipRecorderRing] Ignoruju CLIP – nenahrávám")
                return
            if self._saving:
                print("[ClipRecorderRing] Ignoruju CLIP – už ukládám")
                return
            self._saving = True

        t = threading.Thread(target=self._save_worker, daemon=True)
        t.start()

    def _save_worker(self):
        try:
            # 1) Snapshot bufferu – rychlá operace pod lockem.
            chunks, total_bytes, duration_seconds = self.ring.snapshot()

            ts = time.strftime("%Y%m%d_%H%M%S")
            h264_path = CLIP_DIR / f"clip_{ts}.h264"
            mp4_path = CLIP_DIR / f"clip_{ts}.mp4"
            meta_path = CLIP_DIR / f"clip_{ts}.meta.txt"

            num_chunks = len(chunks)
            # Odhad délky z bajtů (jako dřív)
            approx_seconds_bytes = (total_bytes * 8) / (self.bitrate or 1)

            print(f"[ClipRecorderRing] Ukládám klip (H.264) do {h264_path}")
            print(
                f"[ClipRecorderRing]  chunks={num_chunks}, "
                f"total_bytes={total_bytes}, "
                f"~{approx_seconds_bytes:.2f} s z bajtů, "
                f"~{duration_seconds:.2f} s z timestampů, "
                f"bitrate={self.bitrate}"
            )

            # 2) Zápis H.264 do dočasného souboru
            with open(h264_path, "wb") as f:
                for ch in chunks:
                    f.write(ch)

            # 3) Převod na MP4 pomocí ffmpeg (bez rekomprese, jen remux).
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-f", "h264",
                "-framerate", str(self.fps),
                "-i", str(h264_path),
                "-c", "copy",
                str(mp4_path),
            ]
            print(f"[ClipRecorderRing] Spouštím ffmpeg: {' '.join(ffmpeg_cmd)}")

            try:
                subprocess.run(
                    ffmpeg_cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                ffmpeg_ok = True
            except subprocess.CalledProcessError as e:
                print("[ClipRecorderRing] ffmpeg selhal:", repr(e))
                ffmpeg_ok = False

            # 4) Pokud MP4 vzniklo, H.264 můžeme smazat.
            if ffmpeg_ok and mp4_path.exists():
                print(f"[ClipRecorderRing] MP4 hotové: {mp4_path}, mažu {h264_path}")
                try:
                    h264_path.unlink()
                except Exception as e:
                    print("[ClipRecorderRing] Nepodařilo se smazat .h264:", repr(e))
            else:
                print("[ClipRecorderRing] MP4 se nepodařilo vytvořit, ponechávám .h264")

            # Výsledný soubor (primárně MP4, fallback H.264)
            final_path = mp4_path if ffmpeg_ok and mp4_path.exists() else h264_path
            final_ext = final_path.suffix.lower()

            meta_text = (
                f"timestamp: {ts}\n"
                f"file: {final_path.name}\n"
                f"original_h264: {h264_path.name}\n"
                f"chunks: {num_chunks}\n"
                f"total_bytes: {total_bytes}\n"
                f"bitrate_bps: {self.bitrate}\n"
                f"approx_seconds_from_bytes: {approx_seconds_bytes:.2f}\n"
                f"duration_seconds_from_ts: {duration_seconds:.3f}\n"
                f"format: {final_ext}\n"
                f"play_hint: "
                f"{'ffplay ' if final_ext == '.mp4' else 'ffplay -f h264 -framerate ' + str(self.fps) + ' '}"
                f"{final_path.name}\n"
                f"mp4_hint: ffmpeg -f h264 -framerate {self.fps} -i {h264_path.name} "
                f"-c copy {h264_path.stem}.mp4\n"
            )
            with open(meta_path, "w") as mf:
                mf.write(meta_text)

            self.last_clip_info = {
                "timestamp": ts,
                "path": str(final_path),
                "meta_path": str(meta_path),
                "chunks": num_chunks,
                "total_bytes": total_bytes,
                "approx_seconds_from_bytes": approx_seconds_bytes,
                "duration_seconds_from_ts": duration_seconds,
                "format": final_ext,
            }

            print(f"[ClipRecorderRing] Klip hotový ({final_ext}), meta: {meta_path}")

        except Exception as e:
            print("[ClipRecorderRing] Chyba při ukládání klipu:", repr(e))
        finally:
            with self._lock:
                self._saving = False

    def stop(self):
        """Korektní ukončení při vypnutí programu."""
        try:
            if self._recording:
                self.picam2.stop_recording()
        except Exception:
            pass
        self._recording = False
