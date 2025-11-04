from dataclasses import dataclass, field
from threading import Thread, Event
from queue import Queue
from typing import Optional
from state import State
from cam_event import Cam_Event
from camera_service import Camera_Service
from cross_params import Crosshair_params



@dataclass
class Context:
    fsm_events: Queue = field(default_factory=Queue)
    state: State = State.OFF
    camera: Camera_Service = field(default_factory=Camera_Service)
    cross_params: Crosshair_params = field(default_factory=Crosshair_params)
    window_size: tuple = (640, 480)

    def __post_init__(self):
        self.camera.attach(self)
    
   
