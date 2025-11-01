from dataclasses import dataclass, field
from threading import Thread, Event
from queue import Queue
from typing import Optional
from state import State
from cam_event import Cam_Event

@dataclass
class Context:
    fsm_events: Queue = field(default_factory=Queue)      # GPIO → FSM
    cam_commands: Queue = field(default_factory=Queue)    # FSM → camera
    state: State = State.OFF

    cam_thread: Optional[Thread] = None
    stop_event: Event = field(default_factory=Event)

    def shutdown_camera(self):
        # 1) pošli STOP do workeru (čte-li frontu)
        self.cam_commands.put(Cam_Event.OFF)
        # 2) rozviť STOP event (když zrovna nečte)
        self.stop_event.set()
        # 3) počkej na konec
        if self.cam_thread and self.cam_thread.is_alive():
            self.cam_thread.join(timeout=2.0)
        self.cam_thread = None
        # 4) připrav na další start
        self.stop_event.clear()