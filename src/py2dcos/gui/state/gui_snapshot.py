from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional
from py2dcos.types import InputFile, MathSettings, PlotSettings
from py2dcos.config.resources import CorrType

@dataclass(frozen=True, slots=True)
class GuiSnapshot:
    file1: Optional[InputFile] = None
    file2: Optional[InputFile] = None
    corr_type: CorrType        = CorrType.HOMO
    math: MathSettings         = MathSettings()
    plot: PlotSettings         = PlotSettings()
    show_3d: bool              = False

    def update(self, **kwargs) -> "GuiSnapshot":
        return replace(self, **kwargs)
