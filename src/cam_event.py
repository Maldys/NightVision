from enum import Enum, auto

class Cam_Event(Enum):
    LIVE = auto()
    OFF = auto()
    REC = auto()
    SHOW_OVERLAY = auto()
    HIDE_OVERLAY = auto()
    TOAST = auto()
  
