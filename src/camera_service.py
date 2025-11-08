from threading import Thread, Event, Timer
from queue import Queue, Empty
from picamera2 import Picamera2, Preview, MappedArray
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
      self.overlay_enabled = True
      self.toast = False
      self.toast_text = ""


      
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

    def show_toast(self, text: str):
        self.cmd_queue.put(Cam_Event.TOAST)
        self.toast_text = text




    #vnitrni metody     

    def clear_toast(self):
        self.toast = False
        self.toast_text = ''


    def frame_callback(self, request):
        try:
            if self.cross_params is None or not self.overlay_enabled:
                return

            with MappedArray(request, "main") as m:
                frame = m.array
                h, w = frame.shape[:2] 
            cx = w // 2 - self.ctx.cross_params.x_offset
            cy = h // 2 - self.ctx.cross_params.y_offset


            sz = self.ctx.cross_params.size #size
            th = self.ctx.cross_params.thickness #line thickness

            r, g, b = self.ctx.cross_params.color
            color = (b,g,r)

            cv2.line(frame, (cx - sz, cy), (cx + sz, cy), color, th, lineType=cv2.LINE_AA)
            cv2.line(frame, (cx, cy - sz), (cx, cy + sz), color, th, lineType=cv2.LINE_AA)

            if self.ctx.cross_params.text_to_show:


                text = self.ctx.cross_params.text_to_show
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.8
                thickness = 2

                # Zjistí rozměr textu
                (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

                # Výpočet pozice pro zarovnání na střed
                x = (frame.shape[1] - text_width) // 2

                y_cross_offset = self.ctx.cross_params.y_offset
        
                if y_cross_offset <= 0:
                    y = 120
                else:
                    y = 360
                
                cv2.putText(img = frame,text = text, org = (x,y), fontFace=font, fontScale=font_scale, color=color, thickness=thickness, lineType=cv2.LINE_AA)

            if self.toast and self.toast_text:
                self.toast = False

                t = Timer(2.0, self.clear_toast)
                t.start()


            if self.toast_text:
                text = self.toast_text
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1
                thickness = 2

                # Zjistí rozměr textu
                (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

                # Výpočet pozice pro zarovnání na střed
                x = (frame.shape[1] - text_width) // 2
                y = (frame.shape[0] - text_height) // 2
                                
                cv2.putText(img = frame,text = text, org = (x,y), fontFace=font, fontScale=font_scale, color=color, thickness=thickness, lineType=cv2.LINE_AA)
  


            
            

        except Exception as e:
            print("frame_callback error:", repr(e))
        

    def worker(self):
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_preview_configuration(main={"size": (480,480), "format": "RGB888"},  display="main"))

        self.overlay_enabled = True

        self.picam.post_callback = self.frame_callback

        self.picam.start_preview(Preview.DRM, x = 0, y = 0, width = 480, height = 480) 
        self.picam.start()
        self.running_event.set()
        
        

        alive = True
  


        try:
            while alive and not self.stop_event.is_set():
                try:
                    cmd = self.cmd_queue.get(timeout=0.05)
                except Empty:
                    continue

                if cmd == Cam_Event.LIVE:
                    if not self.running_event.is_set():
                        self.running_event.set()
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
                    self.overlay_enabled = True
                elif cmd == Cam_Event.HIDE_OVERLAY:
                    self.overlay_enabled = False
                elif cmd == Cam_Event.TOAST:
                    self.toast = True

                    
                    
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