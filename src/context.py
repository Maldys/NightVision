from dataclasses import dataclass, field
from threading import Thread, Event
from queue import Queue
from typing import Optional
from state import State
from cam_event import Cam_Event
from camera_worker import camera_worker

@dataclass
class Context:
    fsm_events: Queue = field(default_factory=Queue)      
    cam_commands: Queue = field(default_factory=Queue)    
    state: State = State.OFF

    cam_thread: Optional[Thread] = None
    stop_event: Event = field(default_factory=Event)

    def shutdown_camera(self):
        self.cam_commands.put(Cam_Event.OFF)
        self.stop_event.set()
        if self.cam_thread and self.cam_thread.is_alive():
            self.cam_thread.join(timeout=2.0)
        self.cam_thread = None
        self.stop_event.clear()
        

    def start_camera(self):
        if self.cam_thread == None or not self.cam_thread.is_alive():
            self.stop_event.clear()
            self.cam_thread = Thread(target=camera_worker, args=(ctx,))
            self.cam_thread.start()

        