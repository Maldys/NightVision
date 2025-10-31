from queue import Queue
from state import State
from threading import Thread, Event
from dataclasses import dataclass

@dataclass
class Context:
        fsm_events = Queue()
        cam_comands = Queue()
        state = State.OFF
        cam_thread = None
        
        stop_event = Event()
        

    