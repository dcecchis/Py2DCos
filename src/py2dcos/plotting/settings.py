# src/py2dcos/plotting/settings.py

from dataclasses import dataclass
from enum import Enum, auto

class Peaks(Enum):
    ALL      = auto()
    POSITIVE = auto()
    NEGATIVE = auto()

@dataclass
class PlotSettings:
    """Encapsulate all 2D‐plot parameters in one object."""
    color_map: str             = "coolwarm"
    num_contours: int          = 6
    locator: str               = "linear"
    x_axis: str                = "decreasing"
    color_map_intensity: float = 1.0
    contour_line_color: str    = "black"
    contour_line_alpha: float  = 0.6
    peaks: Peaks               = Peaks.ALL
    sync_diag: str             = "main"
    async_diag: str            = "anti"
