import time
import threading
from pathlib import Path

from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput

CLIP_DIR = Path("/mnt/p3/clips")
CLIP_DIR.mkdir(parents=True, exist_ok=True)


class ClipRecorder:
    def __init__(self, picam2,
                 pre_ms=7000,
                 post_ms=3000,
                 bitrate=5_000_000,
                 fps=20):

        self.picam2 = picam2
        self.pre_ms = pre_ms
        self.post_ms = post_ms
        self.fps = fps
        self._clip_index = 0

        # CircularOutput používá počet snímků, ne milisekundy.
        pre_s = pre_ms / 1000.0
        post_s = post_ms / 1000.0

        # Buffer musí pobrat historii + post + malou rezervu.
        buffersize = int((pre_s + post_s + 1.0) * fps)

        print(f"[ClipRecorder] buffersize={buffersize} frames "
              f"(~{buffersize / fps:.1f} s)")

        self.encoder = H264Encoder(
            bitrate=bitrate,
            framerate=fps,
            enable_sps_framerate=True,
        )

        # Klasický CircularOutput (ověřený a podporovaný)
        self.circular = CircularOutput(buffersize=buffersize)

        self._lock = threading.Lock()
        self._saving = False
        self._recording = False

    def start(self):
        """Spustí kontinuální záznam do kruhového bufferu."""
        if self._recording:
            return
        self.picam2.start_recording(self.encoder, self.circular)
        self._recording = True
        print("[ClipRecorder] recording started into circular buffer")

    def request_clip(self):
        with self._lock:
            if not self._recording:
                print("[ClipRecorder] request_clip: not recording -> IGNORE")
                return
            if self._saving:
                print("[ClipRecorder] request_clip: already saving -> IGNORE")
                return
            self._saving = True

            print("[ClipRecorder] request_clip: starting worker thread")
            threading.Thread(target=self._save_clip_worker, daemon=True).start()


    def _save_clip_worker(self):
        try:
            ts = time.strftime("%Y%m%d_%H%M%S")
            self._clip_index += 1
            filename = CLIP_DIR / f"clip_{ts}_{self._clip_index:03d}.h264"
            print(f"[ClipRecorder] start clip #{self._clip_index} -> {filename}")

            # CircularOutput: nastavíme cílový soubor a pustíme zápis.
            self.circular.fileoutput = str(filename)
            self.circular.start()

            # post_ms = kolik nových snímků po stisku tlačítka
            time.sleep(self.post_ms / 1000.0)

            # stop() = dopíše zbytek bufferu a zavře soubor
            self.circular.stop()

            print("[ClipRecorder] clip done")
        except Exception as e:
            print("[ClipRecorder] error while saving clip:", repr(e))
        finally:
            with self._lock:
                self._saving = False

    def stop(self):
        """Bezpečné ukončení při vypínání aplikace."""
        # krátce počkáme, pokud se právě ukládá klip
        t0 = time.time()
        while True:
            with self._lock:
                if not self._saving:
                    break
            if time.time() - t0 > 5.0:
                print("[ClipRecorder] stop(): still saving, giving up wait")
                break
            time.sleep(0.05)

        try:
            # Pokud by náhodou byl aktivní nějaký výstup
            self.circular.stop()
        except Exception:
            pass

        if self._recording:
            try:
                self.picam2.stop_recording()
            except Exception:
                pass
            self._recording = False
