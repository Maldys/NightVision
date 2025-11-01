from dataclasses import dataclass, field
from threading import Thread, Event
from queue import Queue
from typing import Optional
from state import State
from cam_event import Cam_Event
from camera_service import Camera_Service



@dataclass
class Context:
    fsm_events: Queue = field(default_factory=Queue)
    state: State = State.OFF
    camera: Camera_Service = field(default_factory=Camera_Service)
    current_crs: None
    
   
