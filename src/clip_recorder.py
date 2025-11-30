import time
import threading
from pathlib import Path

from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput2, PyavOutput


CLIP_DIR = Path("/mnt/p3/clips")
CLIP_DIR.mkdir(parents=True, exist_ok=True)


class ClipRecorder:

    def __init__(self, picam2,
                 pre_ms=7000,
                 post_ms=3000,
                 bitrate=5_000_000):

        self.picam2 = picam2
        self.pre_ms = pre_ms
        self.post_ms = post_ms

        # HW H.264 encoder
        self.encoder = H264Encoder(bitrate=bitrate)

        # Kruhový výstup – drží posledních ~pre_ms ms videa
        self.circular = CircularOutput2(buffer_duration_ms=self.pre_ms)

        # Start trvalého záznamu do kruhového bufferu
        # => NEBLOKUJE, běží na pozadí uvnitř Picamera2/libcamera
        self.picam2.start_recording(self.encoder, self.circular)

        # Zámek, aby nešlo spustit dva clipy současně
        self._lock = threading.Lock()
        self._saving = False

    def request_clip(self):

        with self._lock:
            if self._saving:
                return
            self._saving = True

        t = threading.Thread(target=self.save_clip_worker, daemon=True)
        t.start()

    def save_clip_worker(self):
        try:
            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = CLIP_DIR / f"clip_{ts}.mp4"
            print(f"[ClipRecorder] Začínám klip -> {filename}")

            # otevření MP4 výstupu:
            # - okamžitě se přelije obsah kruhového bufferu (cca pre_ms)
            # - dál se streamuje vše nové
            self.circular.open_output(PyavOutput(str(filename)))

            # chceme ještě cca post_ms "po" stisku tlačítka
            time.sleep(self.post_ms / 1000.0)

            # zavření výstupu:
            # - zbylý obsah bufferu se dopíše
            # - soubor se korektně uzavře jako validní MP4
            self.circular.close_output()

            print("[ClipRecorder] Klip hotový")
        except Exception as e:
            print(f"[ClipRecorder] Chyba při ukládání klipu: {e!r}")
        finally:
            with self._lock:
                self._saving = False

    def stop(self):
        """Volitelné – pro korektní ukončení při shutdownu programu."""
        try:
            self.circular.close_output()
        except Exception:
            pass
        try:
            self.picam2.stop_recording()
        except Exception:
            pass
