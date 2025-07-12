from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Tuple, Optional
from py2dcos.config.resources import (
    CorrType, CalcMethod, RefSpectra, Diagonal,
    AxisDirection, ShownGraph, PeaksSigns
)

ExcelParams = Tuple[str, str, str]

@dataclass(frozen=True, slots=True)
class GuiState:
    # data-treatment
    sigma_gaussian: int = 0
    node_attenuation: bool = False
    reconstruction_components: int = 0

    # correlation
    corr_type: CorrType = CorrType.HOMO
    calc_method: CalcMethod = CalcMethod.HT
    ref_spectra: RefSpectra = RefSpectra.INITIAL

    # plotting
    color_map: str = "coolwarm"
    num_contours: int = 6
    locator_choice: str = "linear"
    sync_diag: Diagonal = Diagonal.MAIN
    async_diag: Diagonal = Diagonal.MAIN
    x_axis: AxisDirection = AxisDirection.DECREASING
    color_map_intensity: float = 1.0
    contour_line_color: str = "black"
    contour_lines_intensity: float = 0.6
    shown_graph: ShownGraph = ShownGraph.BOTH
    peaks_signs: PeaksSigns = PeaksSigns.ALL

    # files / misc
    filename1: Optional[Tuple[str, object]] = None
    format1: str = ""
    filename2: Optional[Tuple[str, object]] = None
    format2: str = ""
    excel_params1: Optional[ExcelParams] = None
    excel_params2: Optional[ExcelParams] = None
    show_3d: bool = False

    def with_updates(self, **kwargs) -> "GuiState":
        """Return a new state with selected fields changed."""
        return replace(self, **kwargs)
