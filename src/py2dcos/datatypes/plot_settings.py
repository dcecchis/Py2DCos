from __future__ import annotations
from dataclasses import dataclass, replace
from py2dcos.config.resources import Diagonal, AxisDirection, PeaksSigns, ShownGraph

@dataclass(frozen=True, slots=True)
class PlotSettings:
    color_map: str         = "coolwarm"
    num_contours: int      = 6
    locator: str           = "linear"   # linear | maxN | log
    sync_diag: Diagonal    = Diagonal.MAIN
    async_diag: Diagonal   = Diagonal.MAIN
    x_axis: AxisDirection  = AxisDirection.DECREASING
    color_map_intensity: float = 1.0
    contour_line_color: str  = "black"
    contour_line_alpha: float = 0.6
    peaks: PeaksSigns        = PeaksSigns.ALL
    shown_graph: ShownGraph         = ShownGraph.BOTH     # sync | async | both

    def update(self, **changes) -> "PlotSettings":
        """Return a new PlotSettings with the given fields replaced."""
        return replace(self, **changes)
 