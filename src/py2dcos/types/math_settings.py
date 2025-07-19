from __future__ import annotations
from dataclasses import dataclass, replace
from py2dcos.config.resources import CalcMethod, RefSpectra

@dataclass(frozen=True, slots=True)
class MathSettings:
    method: CalcMethod            = CalcMethod.HT      # HT, FFT
    ref: RefSpectra               = RefSpectra.INITIAL     # ini, end, mean, zero …
    sigma_gaussian: float  = 0.0       # 0 disables smoothing
    node_attenuation: bool = False
    reconstruction_comps: int = 0      # 0 disables PCA reconstruction

    def update(self, **changes) -> "MathSettings":
        """Return a new MathSettings with the given fields replaced."""
        return replace(self, **changes)