from dataclasses import dataclass
from Cross_types import Cross_type

@dataclass
class Crosshair_params:
    type: Cross_type = Cross_type.CROSS
    color: tuple = (0, 255, 0)
    thickness: int = 2
    size: int = 40
    center: tuple = None
    show_text: bool = False
    text: str = "NV"
    text_scale: float = 0.6
    text_thickness: int = 1