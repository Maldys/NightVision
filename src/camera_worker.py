from threading import Thread, Event
import time
from context import Context
from fsm_event import Fsm_Event


def camera_worker(ctx: Context):
    running = True
    while running and not ctx.stop_event.is_set():
        print("Running")
        time.pause(1)

        try:
            cmd = ctx.cam_comands.get()
            state = ctx.state
        except Exception:
            continue


        if cmd == Fsm_Event.PWR_BTN_LONG:
            running = False
