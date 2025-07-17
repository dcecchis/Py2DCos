from __future__ import annotations

"""PyQt5 widget for selecting one or two input files used by Py2DCoS.

This refactor extracts the duplicated logic of the two file‑selection slots
into a single private helper ``_choose_file``.  Behaviour is identical to the
previous version but the code is now DRY and easier to test/extend.
"""

from pathlib import Path
import logging

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QPushButton

from py2dcos.config.resources import CorrType
from .excel_params_dialog import ExcelParamsDialog
from .base_box import BaseBox

logger = logging.getLogger(__name__)


class InputFilesBox(BaseBox):
    """Collapsible section that lets the user pick one or two input files.

    It emits a *flattened* ``dict`` describing the chosen files so that the
    main window can merge those changes into the global ``GuiState``.  Keys:

    ``filename1`` / ``filename2``
        Tuple ``(path, fmt)`` where *fmt* is the lower‑case extension.
    ``format1`` / ``format2``
        String with the extension alone (``csv``, ``txt``, ``xlsx`` …).
    ``excel_params1`` / ``excel_params2``
        Tuple ``(sheet, row, cols, labeled)`` only when *fmt* == ``xlsx``.
    """

    state_changed = pyqtSignal(dict)


    # Qt lifecycle
    def __init__(self, state, parent=None):
        super().__init__("Input", state, parent)

        # primary file
        self.file1_button = QPushButton("Choose your file")
        self.file1_button.setMinimumSize(250, 30)
        self.lay.addWidget(self.file1_button)

        # secondary file (only for heterocorrelation)
        self.file2_button = QPushButton("Choose your file")
        self.file2_button.setMinimumSize(250, 30)
        self.file2_button.hide()
        self.lay.addWidget(self.file2_button)

        # connect both buttons to the same helper via lambda index
        self.file1_button.clicked.connect(lambda: self._choose_file(1))
        self.file2_button.clicked.connect(lambda: self._choose_file(2))

    # Public API 
    def update_from_state(self, state):  # noqa: D401 – Qt callback, no return
        """Synchronise button labels / visibility with the ``GuiState``."""
        if state.filename1:
            self.file1_button.setText(Path(state.filename1[0]).name)

        # show second selector only in hetero‑correlation mode
        self.file2_button.setVisible(state.corr_type is CorrType.HETERO)

        if state.filename2:
            self.file2_button.setText(Path(state.filename2[0]).name)


    def _choose_file(self, idx: int) -> None:
        """Common slot for *both* buttons.

        idx is 1 or 2 and is used to build dynamic payload keys and to
        pick the correct button attribute via getattr
        """
        try:
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Open file",
                "",
                "all files (*);;excel files (*.xlsx);;csv files (*.csv);;txt files (*.txt)",
            )
            if not path:
                return  # user cancelled

            p = Path(path)
            fmt = p.suffix.lstrip(".").lower()

            payload = {f"filename{idx}": (path, fmt), f"format{idx}": fmt}

            # Excel files need extra parameters via a modal dialog
            if fmt == "xlsx":
                dlg = ExcelParamsDialog(path, self)
                if dlg.exec_() != QDialog.Accepted:
                    return  # user aborted Excel‑params dialog
                payload[f"excel_params{idx}"] = dlg.get_params()

            # update button label and tooltip immediately
            button: QPushButton = getattr(self, f"file{idx}_button")
            button.setText(p.name)
            button.setToolTip(path)

            # broadcast state change
            self.state_changed.emit(payload)

        except Exception as exc:  # noqa: BLE001 – want *any* exception logged
            logger.exception("Error selecting file %s", idx)
            QMessageBox.critical(self, "Error loading file", str(exc))
