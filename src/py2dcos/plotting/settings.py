from dataclasses import dataclass
from enum import Enum, auto

@dataclass
# dataclass decorator generates init, repr, and eq methods automatically for this simple container
class PlotSettings:
    """encapsulate all 2d-plot parameters in one object for easy configuration"""
    color_map: str             = "coolwarm"   # default colormap for contour fills
    num_contours: int          = 6            # default number of contour lines
    locator: str               = "linear"     # default algorithm for contour level placement
    x_axis: str                = "decreasing" # default orientation of the x axis values
    color_map_intensity: float = 1.0          # default intensity scaling for colormap
    contour_line_color: str    = "black"      # default color for contour lines
    contour_line_alpha: float  = 0.6          # default transparency for contour lines
    peaks: str                 = "all"        # default setting to show all peaks
    sync_diag: str             = "main"       # default diagonal for synchronous plot
    async_diag: str            = "anti"       # default diagonal for asynchronous plot
