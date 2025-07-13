# gui/state.py

from __future__ import annotations
from dataclasses import dataclass, field, fields, replace
from typing import Tuple, Optional, ClassVar, FrozenSet
from py2dcos.config.resources import (
    CorrType, CalcMethod, RefSpectra, Diagonal,
    AxisDirection, ShownGraph, PeaksSigns
)

ExcelParams = Tuple[str, str, str]

@dataclass(frozen=True, slots=True)
class GuiState:
    # ▸ data-treatment (recompute needed)
    sigma_gaussian: int = field(default=0, metadata={"recalc": True})
    node_attenuation: bool = field(default=False, metadata={"recalc": True})
    reconstruction_components: int = field(default=0, metadata={"recalc": True})

    # ▸ correlation (recompute needed)
    corr_type: CorrType = field(default=CorrType.HOMO, metadata={"recalc": True})
    calc_method: CalcMethod = CalcMethod.HT
    ref_spectra: RefSpectra = field(default=RefSpectra.INITIAL, metadata={"recalc": True})

    # ▸ plotting (no recompute)
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

    # ▸ files / misc
    filename1: Optional[Tuple[str, object]] = None
    format1: str = ""
    filename2: Optional[Tuple[str, object]] = None
    format2: str = ""
    excel_params1: Optional[ExcelParams] = None
    excel_params2: Optional[ExcelParams] = None
    show_3d: bool = False

    def with_updates(self, **kwargs) -> "GuiState":
        return replace(self, **kwargs)

# Now that GuiState exists, compute the class‐level set:
GuiState.requiring_recalc = frozenset(
    f.name for f in fields(GuiState)
    if f.metadata.get("recalc", False)
)
