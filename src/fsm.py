from fsm_event import Fsm_Event
from state import State
from context import Context
from queue import Queue
from cam_event import Cam_Event



class FSM:
    
    def __init__(self, state, transitions, ctx):
        self.state = state
        self.transitions = transitions
        self.ctx: Context = ctx
    

    def handle_trans(self, event):
        key = (self.state, event)
        if key in self.transitions:
            next_state, action = self.transitions[key]
            if not next_state: return
            self.state = next_state
            if action:
                action(next_state, self.ctx)
        elif not key in self.transitions and event == Fsm_Event.PWR_BTN_LONG:
            self.state = State.OFF
            self.ctx.camera.shutdown()
            print('OFF')
            
        
            