from dataclasses import dataclass
from cross_type import Cross_type

@dataclass
class Crosshair_params:
    type: Cross_type = Cross_type.CROSS
    color: tuple = (255, 0, 0) #(R,G,B)
    thickness: int = 2
    size: int = 40
    x_offset: int = 0
    y_offset: int = 0
    text_to_show: str = ''
    scale: int = 1
