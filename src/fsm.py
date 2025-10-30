from event import Event
from state import State

class FSM:
    
    def __init__(self, state, transitions):
        self.state = state
        self.transitions = transitions
    

    def handle_trans(self, event):
        key = (self.state, event)
        if key in self.transitions:
            next_state = self.transitions[key][0]
            if not next_state: return
            self.state = next_state
            self.transitions[key][1](next_state)#spousti funkci
        elif not key in self.transitions and event == Event.PWR_BTN_LONG:
            self.state = State.OFF
            print('OFF')
            
        
            