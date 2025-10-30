
from gpiozero import Button, RotaryEncoder
from signal import pause
from queue import Queue
import time
from fsm import FSM
from event import Event
from transitions import transitions
from state import State

queue = Queue()
       
    


#MENU BTN
menu_btn = Button(5)

def menu_short():
    queue.add(Event.MENU_BTN)

menu_btn.when_released = menu_short

#REC BTN
rec_btn = Button(6)

def rec_short():
    queue.add(Event.REC_BTN)
        
rec_btn.when_released = rec_short

#POWER BTN
power_btn = Button(12, hold_time = 1.5)
power_held = False

def power_short():
    global power_held
    if power_held:
        power_held = False
    else:
        queue.add(Event.PWR_BTN_SHORT)
        
def power_long():
    global power_held
    power_held = True
    queue.add(Event.PWR_BTN_LONG)

power_btn.when_released = power_short
power_btn.when_held = power_long

#ENC_A_BTN
enc_a_btn = Button(22)

def enc_a_short():
    queue.add(Event.ENC_A_BTN)

        
enc_a_btn.when_released = enc_a_short

#ENC_A_LEFT/RIGHT

enc_a = RotaryEncoder(17, 27)

def enc_a_left():
    queue.add(Event.ENC_A_LEFT)


def enc_a_right():
    queue.add(Event.ENC_A_RIGHT)


enc_a.when_rotated_clockwise = enc_a_left
enc_a.when_rotated_counter_clockwise = enc_a_right



fsm = FSM(State.OFF, transitions)


while(True):
    fsm.handle_trans(queue.get_first())



