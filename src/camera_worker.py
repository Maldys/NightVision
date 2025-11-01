from threading import Thread, Event
import time
from context import Context
from cam_event import Cam_Event


def camera_worker(ctx: Context):
    running = True
    while running and not ctx.stop_event.is_set():
        print("Running")
        time.sleep(1)

        try:
            cmd = ctx.cam_commands.get(timeout = 0.1)
            state = ctx.state
        except Exception:
            continue


        if cmd == Cam_Event.OFF:
            ctx.cam_thread.stop_event.set()
            running = False
