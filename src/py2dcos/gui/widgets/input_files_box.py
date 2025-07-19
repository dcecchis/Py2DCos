from __future__ import annotations

"""PyQt5 widget for selecting one or two input files used by Py2DCoS.
"""

from pathlib import Path
import logging
from typing   import Optional
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QPushButton

from py2dcos.config.resources import CorrType
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.types           import InputFile, ExcelParams
from .excel_params_dialog import ExcelParamsDialog
from .base_box import BaseBox

logger = logging.getLogger(__name__)


class InputFilesBox(BaseBox):
    """
    Two file-pickers.  Emits {'file1': InputFile} or {'file2': InputFile}.
    """

    state_changed = pyqtSignal(dict)


    # Qt lifecycle
    def __init__(self, snapshot: GuiSnapshot, parent=None):
        super().__init__("Input", snapshot, parent)

        # primary file
        self.file1_btn = QPushButton("Choose your file")
        self.file1_btn.setMinimumSize(250, 30)
        self.file1_btn.clicked.connect(lambda: self._choose_file(idx=1))
        self.lay.addWidget(self.file1_btn)

        # secondary file (only for heterocorrelation)
        self.file2_btn = QPushButton("Choose your file")
        self.file2_btn.setMinimumSize(250, 30)
        self.file2_btn.hide()
        self.file2_btn.clicked.connect(lambda: self._choose_file(idx=2))
        self.lay.addWidget(self.file2_btn)

        self._apply_snapshot(snapshot)

    # Public API 
    def update_from_snapshot(self, snap: GuiSnapshot):  # noqa: D401 – Qt callback, no return
        super().update_from_snapshot(snap)
        self._apply_snapshot(snap)

    def _apply_snapshot(self, snap: GuiSnapshot):
        if snap.file1:
            self.file1_btn.setText(snap.file1.name)
            self.file1_btn.setToolTip(snap.file1.path)
        if snap.file2:
            self.file2_btn.setText(snap.file2.name)
            self.file2_btn.setToolTip(snap.file2.path)

        # visibility
        self.file2_btn.setVisible(snap.corr_type is CorrType.HETERO)

    def _choose_file(self, idx: int) -> None:
        try:
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Open file",
                "",
                "all files (*);;excel files (*.xlsx);;csv files (*.csv);;txt files (*.txt)",
            )
            if not path:
                return  # user cancelled

            ext = Path(path).suffix.lstrip(".").lower()

            excel_params: Optional[ExcelParams] = None

            # Excel files need extra parameters via a modal dialog
            if ext == "xlsx":
                dlg = ExcelParamsDialog(path, self)
                if dlg.exec_() != QDialog.Accepted:
                    return  # user aborted Excel‑params dialog
                excel_params = dlg.get_params()

            file_obj = InputFile(path=path, extension=ext,
                                 excel_params=excel_params)
            
            # update button immediately
            btn = self.file1_btn if idx == 1 else self.file2_btn
            btn.setText(Path(path).name)
            btn.setToolTip(path)

            # emit delta
            self.state_changed.emit({f"file{idx}": file_obj})

        except Exception as exc:  # noqa: BLE001 – want *any* exception logged
            logger.exception("Error selecting file %s", idx)
            QMessageBox.critical(self, "Error loading file", str(exc))
