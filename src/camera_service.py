from threading import Thread, Event
from queue import Queue, Empty
from picamera2 import Picamera2, Preview
import time
from cam_event import Cam_Event

class Camera_Service:
    def __init__(self):
      self.thread = None
      self.cmd_queue = Queue()
      self.stop_event = Event()
      self.running_event = Event()
      self.picam = None
      self.overlay_enabled = False
      self.redo_overlay = False

    #z venku volatelne metody
    def live(self):
        if self.thread is None or not self.thread.is_alive():
            self.clear_queue()
            self.stop_event.clear()
            self.thread = Thread(target=self.worker, daemon=True)
            self.thread.start()
        self.cmd_queue.put(Cam_Event.LIVE)

    def shutdown(self):
        self.cmd_queue.put(Cam_Event.OFF)
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        self.thread = None

    def show_overlay(self):
        self.cmd_queue.put(Cam_Event.SHOW_OVERLAY)
    
    def hide_overlay(self):
        self.cmd_queue.put(Cam_Event.HIDE_OVERLAY)

    def update_overlay(self):
        self.cmd_queue.put(Cam_Event.UPDATE_OVERLAY)

    #vnitrni metody
    def worker(self):
        config = self.picam.create_preview_configuration(
        main={"size": (1280, 720), "format": "RGB888"}
        )
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_preview_configuration(config))
        self.picam.start_preview(Preview.DRM) 
        self.picam.start()
        self.running_event.set()

        alive = True

        try:
            while alive and not self.stop_event.is_set():
                try:
                    cmd = cmd_queue.get(timeout=0.05)
                except:
                    continue

                if cmd == Cam_Event.LIVE:
                    if not self.running_event.is_set():
                        self.picam.running_event.set()
                        self.picam.start()

                elif cmd == Cam_Event.OFF:
                    if self.running_event.is_set():
                        try: 
                            self.picam.stop_preview()
                        except Exception: 
                            pass
                        try: 
                            self.picam.stop()
                        except Exception: 
                            pass
                        self.running_event.clear()
                    alive = False
                elif cmd == Cam_Event.SHOW_OVERLAY:
                    overlay_enabled = True
                elif cmd == Cam_Event.HIDE_OVERLAY:
                    overlay_enabled = False
                elif cmd == Cam_Event.UPDATE_OVERLAY:
                    redo_overlay = True
                    
        finally:
            if self.picam:
                    try: self.picam.stop_preview()
                    except Exception: pass
                    try: self.picam.stop()
                    except Exception: pass
                    try: self.picam.close()
                    except Exception: pass
            self.picam = None
            self.running_event.clear()


    def clear_queue(self):
        try:
            while True:
                self.cmd_queue.get_nowait()
        except Empty:
            pass