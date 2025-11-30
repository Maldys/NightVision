from threading import Thread, Event, Timer
from queue import Queue, Empty
from picamera2 import Picamera2, Preview, MappedArray
import time
from cam_event import Cam_Event
import numpy as np
import cv2
from cross_type import Cross_type
from collections import deque
import os

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
      self.fps = 30
      self.clip = False
      self.pre_buffer = None
      self.post_buffer = None
      self.clip_time = None
      self.final_buffer = None


      
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

    def make_clip(self):
        self.cmd_queue.put(Cam_Event.CLIP)




    #vnitrni metody     

    def clear_toast(self):
        self.toast = False
        self.toast_text = ''

    def make_rectangle(self, frame, x, y, offset, thickness, text_width, text_height):
        xr = x - offset
        yr = y + offset

        cv2.rectangle(frame, (xr, yr), (xr + offset*2 + text_width, yr - offset*2 - text_height),(211, 211, 211),-1)
        cv2.rectangle(frame, (xr-thickness, yr+thickness), (xr + offset*2 + text_width, yr - offset*2 - text_height),0,thickness)

    def get_fps(self):
        metadata = self.picam.capture_metadata()
        frame_duration_us = metadata["FrameDuration"]
        fps = 1_000_000 // frame_duration_us
        self.fps = fps
        print(fps)

    def start_post(self):
        self.clip = True
        self.final_buffer = list(self.pre_buffer)
        if self.post_buffer is not None:
            self.post_buffer.clear()
        self.clip_time = time.monotonic()
         

    def make_pre_buffer(self):
        self.get_fps()
        self.pre_buffer = deque(maxlen=7*self.fps)

    def make_post_buffer(self):
        self.get_fps()
        self.post_buffer = deque(maxlen=3*self.fps)

    def save_clip_thread(self, frames):
        if not frames:
            print("save_clip_thread: empty frames, nothing to save")
            return

        first = frames[0]
        if first is None or not hasattr(first, "shape"):
            print("save_clip_thread: invalid first frame:", type(first))
            return

        height, width = first.shape[:2]
        fps = float(self.fps)

        out_dir = "/mnt/p3/clips"   # podle tebe existuje
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"clip_{timestamp}.mp4"
        filepath = os.path.join(out_dir, filename)

        cmd = [
            "ffmpeg",
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-pix_fmt", "bgr24",
            "-s", f"{width}x{height}",
            "-r", str(fps),
            "-i", "-",
            "-an",
            "-c:v", "libx264",        # nebo "h264_v4l2m2m" pokud HW enkodér bude fungovat
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            filepath,
        ]

        print(
            "save_clip_thread: running:",
            " ".join(cmd),
            f"(frames={len(frames)}, fps={fps}, size={width}x{height})"
        )

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,   # pro debug můžeš dát None
        )

        try:
            for f in frames:
                if f is None:
                    continue
                buf = np.asarray(f, dtype=np.uint8).tobytes()
                proc.stdin.write(buf)
        except Exception as e:
            print("save_clip_thread: error while writing frames:", repr(e))
        finally:
            try:
                proc.stdin.close()
            except Exception:
                pass
            ret = proc.wait()

        if ret != 0:
            print("save_clip_thread: ffmpeg exited with code", ret)
        else:
            print("save_clip_thread: done", filepath)

    def save_clip(self, frames):

        if not frames:
            print("save_clip: empty frames, nothing to save")
            return

        try:
            frames_copy = [f.copy() for f in frames if f is not None]
        except Exception as e:
            print("save_clip: cannot copy frames:", repr(e))
            return

    
        t = threading.Thread(
            target=self._save_clip_thread,
            args=(frames_copy,),
            daemon=True
        )
        t.start()

        print(f"save_clip: started background save, frames={len(frames_copy)}")
    




        
    def clear_queue(self):
        try:
            while True:
                self.cmd_queue.get_nowait()
        except Empty:
            pass


    def frame_callback(self, request):
        try:
            if self.cross_params is None or not self.overlay_enabled:
                return

            with MappedArray(request, "main") as m:
                frame = m.array
                h, w = frame.shape[:2] 
            
            if self.pre_buffer is not None:
                self.pre_buffer.append(frame)

            if self.clip and self.post_buffer is not None:
                self.post_buffer.append(frame)

            if self.clip and self.clip_time + 3.0 <= time.monotonic() and self.clip_time is not None:
                self.clip = False
                frames_to_save = self.final_buffer + list(self.post_buffer)
                Thread(target=self.save_clip, args=(frames_to_save,), daemon=True).start()

            




            cx = w // 2 - self.ctx.cross_params.x_offset
            cy = h // 2 - self.ctx.cross_params.y_offset


            sz = self.ctx.cross_params.size #size
            th = self.ctx.cross_params.thickness #line thickness

            r, g, b = self.ctx.cross_params.color
            color = (b,g,r)

            if self.ctx.cross_params.cross_type == Cross_type.CROSS:
                cv2.line(frame, (cx - sz, cy), (cx + sz, cy), color, th, lineType=cv2.LINE_AA)
                cv2.line(frame, (cx, cy - sz), (cx, cy + sz), color, th, lineType=cv2.LINE_AA)
            elif self.ctx.cross_params.cross_type == Cross_type.HALO:
                cv2.circle(frame, (cx, cy), 5, color, thickness=-1)
                cv2.circle(frame, (cx, cy), 40, color, th)
            elif self.ctx.cross_params.cross_type == Cross_type.DOT:
                cv2.circle(frame, (cx, cy), 10, color, thickness=-1)

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

                
                self.make_rectangle(frame, x, y, 20, 2, text_width, text_height)

                cv2.putText(img = frame,text = text, org = (x,y), fontFace=font, fontScale=font_scale, color=0, thickness=thickness, lineType=cv2.LINE_AA)

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
                y = (frame.shape[0] + text_height) // 2

                self.make_rectangle(frame, x, y, 30, 2, text_width, text_height)

            
                cv2.putText(img = frame,text = text, org = (x,y), fontFace=font, fontScale=font_scale, color=0, thickness=thickness, lineType=cv2.LINE_AA)
  


            
            

        except Exception as e:
            print("frame_callback error:", repr(e))
        

    def worker(self):
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_preview_configuration(main={"size": (480,480), "format": "RGB888"},  display="main"))
        

        self.overlay_enabled = True

        self.picam.post_callback = self.frame_callback

        self.picam.start_preview(Preview.DRM, x = 0, y = 0, width = 480, height = 480) 
        self.picam.start()
        self.picam.set_controls({"FrameRate": 30})
        self.running_event.set()

        time.sleep(1)

        self.make_pre_buffer()
        self.make_post_buffer()
        
        
        

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
                            self.picam2.close()
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
                elif cmd == Cam_Event.CLIP:
                    self.clip = True
                    self.start_post()

                    
                    
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


    