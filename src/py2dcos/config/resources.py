"""
resources.py
-------------
Central repository for GUI defaults and shared resources.
This file must stay lightweight: no PyQt or Matplotlib imports here.
"""

from enum import Enum, auto
from dataclasses import dataclass

# public constants: lists for combo-box defaults
COLOR_LIST = [
    "navy", "black", "white", "red", "lime", "blue", "yellow",
    "maroon", "olive", "green", "teal",
]

# available colormaps for contour filling
CMAP_LIST = [
    "bwr", "PiYG", "PRGn", "BrBG", "PuOr", "RdGy", "RdBu",
    "RdYlBu", "RdYlGn", "Spectral", "coolwarm", "seismic",
]

# locator algorithms for contour placement
LOCATOR_CHOICES = ["linear", "maxN", "log"]

# numeric bounds for contour counts and intensity sliders
MIN_CONTOURS = 1
MAX_CONTOURS = 40
MIN_INTENSITY = 0
MAX_INTENSITY = 100
MIN_LINE_INTENSITY = 0
MAX_LINE_INTENSITY = 100

# enums define discrete configuration options to avoid magic strings

class CorrType(Enum):
    # choose between same-file vs two-file correlation
    HOMO = "homo"
    HETERO = "hetero"

class CalcMethod(Enum):
    # methods for computing correlation: hilbert or fft
    HT = "HT"
    FFT = "FFT"

class RefSpectra(Enum):
    # reference spectrum choices for baseline correction
    MEAN = "mean"
    ZERO = "zero"
    INITIAL = "ini"
    FINAL = "end"

class Diagonal(Enum):
    # diagonal selection for synchronous/asynchronous plots
    MAIN = "main"
    ANTI = "anti"

class AxisDirection(Enum):
    # x-axis orientation options
    INCREASING = "increasing"
    DECREASING = "decreasing"

class ShownGraph(Enum):
    # which plot(s) to display by default
    SYNC = "sync"
    ASYNC = "async"
    BOTH = "both"

class PeaksSigns(Enum):
    # filter for showing positive, negative, or all peaks
    POSITIVE = "positive"
    NEGATIVE = "negative"
    ALL = "all"
