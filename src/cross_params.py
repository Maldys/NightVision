from dataclasses import dataclass
from cross_type import Cross_type

@dataclass
class Crosshair_params:
    cross_type: Cross_type = Cross_type.DOT
    color: tuple = (255, 0, 0) #(R,G,B)
    thickness: int = 2
    scale: float = 1.0
    size: int = 40
    x_offset: int = 0
    y_offset: int = 0
    
