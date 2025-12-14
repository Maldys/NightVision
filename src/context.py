from dataclasses import dataclass, field
from threading import Thread, Event
from queue import Queue
from typing import Optional
from state import State
from cam_event import Cam_Event
from camera_service import Camera_Service
from cross_params import Crosshair_params
from context_saver import Context_saver
from mode import Mode



@dataclass
class Context:
    fsm_events: Queue = field(default_factory=Queue)
    init_state: State = State.OFF #init state
    mode: Mode = Mode.DAY
    sel_cross: int = 0
    text_to_show = ''
    camera: Camera_Service = field(default_factory=Camera_Service)
    cross_params: Crosshair_params = field(default_factory=lambda: [Crosshair_params() for _ in range(5)])
    context_saver: Context_saver = field(init=False)



    def __post_init__(self):
        self.camera.attach(self)
        self.context_saver = Context_saver(self)
        
    
   
