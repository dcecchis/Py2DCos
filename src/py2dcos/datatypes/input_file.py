from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

ExcelParams = Tuple[str, str, str, bool]    # sheet, cols, rows, labeled.

@dataclass(frozen=True, slots=True)
class InputFile:
    path: str
    extension: str                                       
    excel_params: Optional[ExcelParams] = None           # only for xlsx

    @property
    def name(self) -> str:
        return Path(self.path).name
