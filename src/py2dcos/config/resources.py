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


MIN_CONTOURS = 1
MAX_CONTOURS = 40
MIN_INTENSITY = 0
MAX_INTENSITY = 100
MIN_LINE_INTENSITY = 0
MAX_LINE_INTENSITY = 100


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