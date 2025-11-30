
from gpiozero import Button, RotaryEncoder
from signal import pause
from queue import Queue
import time
from fsm import FSM
from fsm_event import Fsm_Event
from transitions import transitions
from state import State
from context import Context
from threading import Thread
import subprocess
import os


def kill_other_instances():
    this_pid = os.getpid()

    try:
        output = subprocess.check_output(["pgrep", "-f", "main.py"]).decode().strip()
        pids = output.split("\n")

        for pid in pids:
            pid = pid.strip()
            if not pid.isdigit():
                continue

            pid = int(pid)

            if pid == this_pid:
                continue

            try:
                os.kill(pid, 9)
                print(f"Killed old instance PID {pid}")
            except ProcessLookupError:
                pass

    except subprocess.CalledProcessError:
        pass



kill_other_instances()
ctx = Context()
      


#MENU BTN
menu_btn = Button(12,bounce_time=0.05)

def menu_short():
    ctx.fsm_events.put(Fsm_Event.MENU_BTN)

menu_btn.when_released = menu_short

#REC BTN
rec_btn = Button(6, bounce_time=0.05)

def rec_short():
    ctx.fsm_events.put(Fsm_Event.REC_BTN)
        
rec_btn.when_released = rec_short

#POWER BTN
power_btn = Button(5, hold_time = 1.5,bounce_time=0.05)
power_held = False

def power_short():
    global power_held
    if power_held:
        power_held = False
    else:
        ctx.fsm_events.put(Fsm_Event.PWR_BTN_SHORT)
        
def power_long():
    global power_held
    power_held = True
    ctx.fsm_events.put(Fsm_Event.PWR_BTN_LONG)

power_btn.when_released = power_short
power_btn.when_held = power_long

#ENC_A_BTN
enc_a_btn = Button(22,bounce_time=0.05)

def enc_a_short():
    ctx.fsm_events.put(Fsm_Event.ENC_A_BTN)

        
enc_a_btn.when_released = enc_a_short

#ENC_A_LEFT/RIGHT

enc_a = RotaryEncoder(17, 27)

def enc_a_left():
    ctx.fsm_events.put(Fsm_Event.ENC_A_LEFT)


def enc_a_right():
    ctx.fsm_events.put(Fsm_Event.ENC_A_RIGHT)


enc_a.when_rotated_clockwise = enc_a_left
enc_a.when_rotated_counter_clockwise = enc_a_right



fsm = FSM(State.OFF, transitions, ctx)


while(True):
    fsm.handle_trans(ctx.fsm_events.get())
    



