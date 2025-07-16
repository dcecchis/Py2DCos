from __future__ import annotations
from dataclasses import dataclass, field, fields, replace
from typing import Tuple, Optional
from py2dcos.config.resources import (
    CorrType, CalcMethod, RefSpectra, Diagonal,
    AxisDirection, ShownGraph, PeaksSigns
)

# alias for parameters needed when reading excel files (sheet, header row, data range)
ExcelParams = Tuple[str, str, str]

@dataclass(frozen=True, slots=True)
# dataclass auto-generates init, repr, eq and enforces immutability; slots reduce memory footprint
class GuiState:
    # fields that trigger full data/model rebuild when changed
    sigma_gaussian: int = field(default=0, metadata={"rebuild": True})
    node_attenuation: bool = field(default=False, metadata={"rebuild": True})
    reconstruction_components: int = field(default=0, metadata={"rebuild": True})

    # correlation settings (some require rebuild, calc_method only changes algorithm)
    corr_type: CorrType = field(default=CorrType.HOMO, metadata={"rebuild": True})
    calc_method: CalcMethod = CalcMethod.HT # still no FT implemented
    ref_spectra: RefSpectra = field(default=RefSpectra.INITIAL, metadata={"rebuild": True})

    # plotting parameters (controls style only, no model recompute)
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

    # file inputs and misc flags (free to change without triggering rebuild)
    filename1: Optional[Tuple[str, object]] = None
    format1: str = ""
    filename2: Optional[Tuple[str, object]] = None
    format2: str = ""
    excel_params1: Optional[ExcelParams] = None
    excel_params2: Optional[ExcelParams] = None
    show_3d: bool = False  # toggle between 2d canvas and 3d webview

    def with_updates(self, **kwargs) -> "GuiState":
        # create a new state instance merging provided changes
        # preserves immutability by returning a fresh object
        return replace(self, **kwargs)

# compute the set of field names that require full rebuild when updated
GuiState.requiring_rebuild = frozenset(
    f.name for f in fields(GuiState) if f.metadata.get("rebuild", False)
)
# frozenset ensures the set is immutable and optimized for membership checks
