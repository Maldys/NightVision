from threading import Thread, Event, Timer
from queue import Queue, Empty
from picamera2 import Picamera2, Preview, MappedArray
import time
from cam_event import Cam_Event
import numpy as np
import cv2
from cross_type import Cross_type
from clip_recorder import ClipRecorderRing
from mode import Mode


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
        self.fps = 20
        self.clip_recorder = None

        self.ctx = None
        self.cross_params = None

    def attach(self, ctx):
        self.ctx = ctx
        self.cross_params = ctx.cross_params

    # z venku volatelne metody
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
    
    def change_mode(self):
        self.cmd_queue.put(Cam_Event.MODE)
    


    

    # vnitrni metody
    def clear_toast(self):
        self.toast = False
        self.toast_text = ''
    

    def set_mode(self):
        mode = self.ctx.mode
        if(mode == Mode.DAY):
            self.picam.set_controls({
                "AeEnable": True,
                "AwbEnable": True,
                "Saturation": 1.0,
                "Contrast": 1.0,
                "ExposureTime": 0,        
                "AnalogueGain": 0.0,
                "Brightness": 0.0,
            })
        else:
            self.picam.set_controls({
                "AeEnable": False,
                "ExposureTime": 40000,      # 40 ms
                "AnalogueGain": 12.0,       # vysoký gain
                "AwbEnable": False,         # vypnout AWB (jinak hýbe barvami)
                "ColourGains": (1.0, 1.0),
                "Saturation": 0.0,
                "Sharpness": 0.0,
                "Contrast": 1.0,               
                "Brightness": 0.1,
            })

            
            

    def make_rectangle(self, frame, x, y, offset, thickness, text_width, text_height):
        xr = x - offset
        yr = y + offset
        cv2.rectangle(
            frame,
            (xr, yr),
            (xr + offset * 2 + text_width, yr - offset * 2 - text_height),
            (211, 211, 211),
            -1,
        )
        cv2.rectangle(
            frame,
            (xr - thickness, yr + thickness),
            (xr + offset * 2 + text_width, yr - offset * 2 - text_height),
            0,
            thickness,
        )

    def get_fps(self):
        metadata = self.picam.capture_metadata()
        frame_duration_us = metadata["FrameDuration"]
        fps = 1_000_000 // frame_duration_us
        self.fps = fps
        print(fps)

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

            scale = self.ctx.cross_params[self.ctx.sel_cross].scale


            if self.ctx.mode == Mode.NIGHT:
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                gray = np.clip(gray.astype(np.float32) * 1.4, 0, 255).astype(np.uint8)
                frame[:, :, 0] = gray
                frame[:, :, 1] = gray
                frame[:, :, 2] = gray
            


                
            if scale >= 0.75:
                    new_w = int(w / scale)
                    new_h = int(h / scale)

                    x0 = (w - new_w) // 2
                    y0 = (h - new_h) // 2
                    x1 = x0 + new_w
                    y1 = y0 + new_h

                    cropped = frame[y0:y1, x0:x1]
                    zoomed = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

                    frame[:] = zoomed

            cx = w // 2 - self.ctx.cross_params[self.ctx.sel_cross].x_offset
            cy = h // 2 - self.ctx.cross_params[self.ctx.sel_cross].y_offset

            sz = int(self.ctx.cross_params[self.ctx.sel_cross].size)  # size
            th = self.ctx.cross_params[self.ctx.sel_cross].thickness  # line thickness

            r, g, b = self.ctx.cross_params[self.ctx.sel_cross].color
            color = (b, g, r)

            if self.ctx.cross_params[self.ctx.sel_cross].cross_type == Cross_type.CROSS:
                cv2.line(frame, (cx - sz, cy), (cx + sz, cy), color, th, lineType=cv2.LINE_AA)
                cv2.line(frame, (cx, cy - sz), (cx, cy + sz), color, th, lineType=cv2.LINE_AA)
            elif self.ctx.cross_params[self.ctx.sel_cross].cross_type == Cross_type.HALO:
                cv2.circle(frame, (cx, cy), 5, color, thickness=-1)
                cv2.circle(frame, (cx, cy), 40, color, th)
            elif self.ctx.cross_params[self.ctx.sel_cross].cross_type == Cross_type.DOT:
                cv2.circle(frame, (cx, cy), 10, color, thickness=-1)

            if self.ctx.text_to_show:

                text = self.ctx.text_to_show
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.8
                thickness = 2

                # Zjistí rozměr textu
                (text_width, text_height), baseline = cv2.getTextSize(
                    text, font, font_scale, thickness
                )

                # Výpočet pozice pro zarovnání na střed
                x = (frame.shape[1] - text_width) // 2

                y_cross_offset = self.ctx.cross_params[self.ctx.sel_cross].y_offset

                if y_cross_offset <= 0:
                    y = 120
                else:
                    y = 360

                self.make_rectangle(frame, x, y, 20, 2, text_width, text_height)

                cv2.putText(
                    img=frame,
                    text=text,
                    org=(x, y),
                    fontFace=font,
                    fontScale=font_scale,
                    color=0,
                    thickness=thickness,
                    lineType=cv2.LINE_AA,
                )

            if self.toast and self.toast_text:
                self.toast = False
                t = Timer(2.0, self.clear_toast)
                t.start()

            if self.toast_text:
                text = self.toast_text
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1
                thickness = 2

                (text_width, text_height), baseline = cv2.getTextSize(
                    text, font, font_scale, thickness
                )

                x = (frame.shape[1] - text_width) // 2
                y = (frame.shape[0] + text_height) // 2

                self.make_rectangle(frame, x, y, 30, 2, text_width, text_height)

                cv2.putText(
                    img=frame,
                    text=text,
                    org=(x, y),
                    fontFace=font,
                    fontScale=font_scale,
                    color=0,
                    thickness=thickness,
                    lineType=cv2.LINE_AA,
                )

                


        except Exception as e:
            print("frame_callback error:", repr(e))

    def worker(self):
        tuning = Picamera2.load_tuning_file("/usr/share/libcamera/ipa/rpi/vc4/imx708_noir.json")
        self.picam = Picamera2(tuning=tuning)
        config = self.picam.create_video_configuration(
            main={"format": "RGB888", "size": (640, 640)},
            lores={"format": "YUV420", "size": (640, 480)},
            encode="lores",
            display="main"
        )
        self.picam.configure(config)

        self.overlay_enabled = True

        self.picam.post_callback = self.frame_callback

        self.picam.start_preview(Preview.DRM, x=0, y=0, width=480, height=480)
        self.picam.start()
        self.running_event.set()
        self.picam.set_controls({"FrameRate": self.fps})
        self.clip_recorder = ClipRecorderRing(
        self.picam,
        seconds=10,
        bitrate=5_000_000,
        fps=self.fps)
        self.set_mode()
        self.clip_recorder.start()

        self.ctx.context_saver.ctx_from_config()

        time.sleep(1)

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
                            self.picam.close()
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
                    if self.clip_recorder:
                        self.clip_recorder.request_clip()
                
                elif cmd == Cam_Event.MODE:
                    self.set_mode()
                    
                
               

        finally:
            if self.picam:
                try:
                    self.picam.stop_preview()
                except Exception:
                    pass
                try:
                    if self.clip_recorder:
                        self.clip_recorder.stop()
                except Exception:
                    pass
                try:
                    self.picam.stop()
                except Exception:
                    pass
                try:
                    self.picam.close()
                except Exception:
                    pass
            self.picam = None
            self.running_event.clear()
