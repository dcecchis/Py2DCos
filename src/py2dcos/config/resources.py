"""
resources.py
-------------
Central repository for GUI defaults and shared resources.
This file must stay lightweight: no PyQt or Matplotlib imports here.
"""

from enum import Enum, auto
from dataclasses import dataclass

#  PUBLIC CONSTANTS (lists for combo-boxes etc.)
COLOR_LIST = [
    "navy", "black", "white", "red", "lime", "blue", "yellow",
    "maroon", "olive", "green", "teal",
]

CMAP_LIST = [
    "bwr", "PiYG", "PRGn", "BrBG", "PuOr", "RdGy", "RdBu",
    "RdYlBu", "RdYlGn", "Spectral", "coolwarm", "seismic",
]

LOCATOR_CHOICES = ["linear", "maxN", "log"]


#  ENUMS  (categorical settings -- safer than raw strings)
class CorrType(Enum):
    HOMO = "homo"
    HETERO = "hetero"


class CalcMethod(Enum):
    HT = "HT"
    FFT = "FFT"         


class RefSpectra(Enum):
    MEAN = "mean"
    ZERO = "zero"
    INITIAL = "ini"
    FINAL = "end"


class Diagonal(Enum):
    MAIN = "main"
    ANTI = "anti"


class AxisDirection(Enum):
    INCREASING = "increasing"
    DECREASING = "decreasing"


class ShownGraph(Enum):
    SYNC = "sync"
    ASYNC = "async"
    BOTH = "both"


class PeaksSigns(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    ALL = "all"


#  GUI STATE  (single source of truth for defaults)
@dataclass
class GuiState:
    # ▸ data-treatment
    sigma_gaussian: int = 0
    node_attenuation: bool = False
    reconstruction_components: int = 0

    # ▸ correlation
    corr_type: CorrType = CorrType.HOMO
    calc_method: CalcMethod = CalcMethod.HT
    ref_spectra: RefSpectra = RefSpectra.INITIAL

    # ▸ plot configuration
    color_map: str = "coolwarm"
    num_of_contours: int = 6
    locator_choice: str = "linear"
    sync_diag: Diagonal = Diagonal.MAIN
    async_diag: Diagonal = Diagonal.MAIN
    x_axis: AxisDirection = AxisDirection.DECREASING
    color_map_intensity: float = 1.0
    contour_line_color: str = "black"
    contour_lines_intensity: float = 0.6
    shown_graph: ShownGraph = ShownGraph.BOTH
    peaks_signs: PeaksSigns = PeaksSigns.ALL

    # ▸ misc
    canvas: bool = True
    figure: str = ""
