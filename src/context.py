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
from gpiozero import PWMLED



@dataclass
class Context:
    fsm_events: Queue = field(default_factory=Queue)
    init_state: State = State.OFF #init state
    mode: Mode = Mode.NIGHT
    sel_cross: int = 0
    text_to_show = ''
    camera: Camera_Service = field(default_factory=Camera_Service)
    cross_params: Crosshair_params = field(default_factory=lambda: [Crosshair_params() for _ in range(5)])
    context_saver: Context_saver = field(init=False)
    ir_level: float = 0.0
    pwm_ir = PWMLED(18, initial_value=ir_level)
    ir_x_zoom = False #0 = ir, 1 = zoom
    


    def __post_init__(self):
        self.camera.attach(self)
        self.context_saver = Context_saver(self)
        
    
   