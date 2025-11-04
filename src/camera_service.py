from threading import Thread, Event
from queue import Queue, Empty
from picamera2 import Picamera2, Preview
import time
from cam_event import Cam_Event
import numpy as np
import cv2

class Camera_Service:
    def __init__(self):
      self.thread = None
      self.cmd_queue = Queue()
      self.stop_event = Event()
      self.running_event = Event()
      self.picam = None
      self.overlay_enabled = False
      self.redo_overlay = False
      
      self.ctx = None
      self.cross_params = None

    def attach(self, ctx):
        self.ctx = ctx
        self.cross_params = ctx.cross_params
    

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
        self.make_overlay

    #vnitrni metody

    def make_overlay(self) :
        w, h = self.ctx.window_size

        rgba = np.zeros((h, w, 4), dtype=np.uint8)

        if self.cross_params is None:
            return rgba
        
        r, g, b = self.cross_params.color

        alpha = rgba[:, :, 3]
    
        alpha_c = np.ascontiguousarray(alpha)

        cx = w // 2 + self.ctx.cross_params.x_offset
        cy = h // 2 + self.ctx.cross_params.y_offset

        sz = self.ctx.cross_params.size #size
        th = self.ctx.cross_params.thickness #line thickness

        cv2.line(alpha_c, (cx - sz, cy), (cx + sz, cy), 255, th, lineType=cv2.LINE_AA)
        cv2.line(alpha_c, (cx, cy - sz), (cx, cy + sz), 255, th, lineType=cv2.LINE_AA)

        rgba[:, :, 3] = alpha_c

        mask = alpha_c > 0
        rgba[:, :, 0][mask] = r  # R
        rgba[:, :, 1][mask] = g  # G
        rgba[:, :, 2][mask] = b  # B


        return rgba
        

    def worker(self):
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_preview_configuration(main={"size": self.ctx.window_size, "format": "RGB888"}))
        self.picam.start_preview(Preview.DRM) 
        self.picam.start()
        self.running_event.set()
        overlay = self.make_overlay()
        self.picam.set_overlay(overlay)

        alive = True
        overlay = None


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