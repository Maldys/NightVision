from gpiozero import PWMLED, Button, RotaryEncoder
from gpiozero.tools import random_values
from signal import pause

led = PWMLED(18)
btn = Button(23, pull_up=True, bounce_time=0.02)
enc = RotaryEncoder(27, 22)

val = 0

def clamp(x, lo, hi):
    return max(lo, min(x, hi))


def on_press():
    print(val)
    

def decrement():
    global val
    val = clamp(val-1, -100, 100)
    if enc.value >= 0 and enc.value <= 1:
        led.value = enc.value

def increment():
    global val
    val = clamp(val+1, -100, 100)
    if enc.value >= 0 and enc.value <= 1:
        led.value = enc.value

btn.when_pressed = on_press
enc.when_rotated_counter_clockwise = decrement
enc.when_rotated_clockwise = increment
led.value = enc.value


pause()