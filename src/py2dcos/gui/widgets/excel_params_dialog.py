"""
excel_params_dialog.py

modal dialog that asks for excel parsing parameters: sheet name, starting row and column range
"""
from __future__ import annotations

import logging
from typing import Optional, Tuple, List

import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout,
    QLabel, QRadioButton, QComboBox, QLineEdit,
    QButtonGroup, QPushButton, QMessageBox, QWidget
)

from py2dcos.core.validators import (
    validate_special_case, InvalidExcelFormatError
)

logger = logging.getLogger(__name__)


class ExcelParamsDialog(QDialog):
    """
    dialog for selecting excel parsing parameters

    base case: take first sheet with no row or column limits
    special case: let user specify sheet, starting row, and column range
    """

    def __init__(self, excel_path: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setModal(True)
        self.excel_path = excel_path

        # load sheet names so user can pick from actual options
        try:
            self.sheets = pd.ExcelFile(excel_path).sheet_names
        except Exception as exc:          # pragma: no cover
            logger.exception("failed to read excel file %s", excel_path)
            QMessageBox.critical(self, "excel read error", str(exc))
            self.reject()
            return

        # widgets that are only shown in special-case mode
        self._special_widgets: List[QWidget] = []
        # map control keys to their widgets for retrieving values
        self.controls: dict[str, QWidget] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        # set fonts for title and body text
        font_title = QFont("Arial", 12, QFont.Bold)
        font_body  = QFont("Arial", 10)

        self.setWindowTitle("Excel File Options")
        main_vbox = QVBoxLayout(self)

        # header label for dialog title
        header = QLabel("Excel File Options")
        header.setFont(font_title)
        header.setAlignment(Qt.AlignCenter)
        main_vbox.addWidget(header)

        # radio buttons for choosing base vs special case
        self.base_rb    = QRadioButton("Base Case (no extra spec)")
        self.special_rb = QRadioButton("Special Case (specify)")
        for rb in (self.base_rb, self.special_rb):
            rb.setFont(font_body)
            main_vbox.addWidget(rb)
        self.base_rb.setChecked(True)

        # grid layout for special-case inputs
        grid = QGridLayout()
        rows = [
            ("Sheet Name",   QComboBox, self.sheets),
            ("Starting Row", QLineEdit, None),
            ("Column Range", QLineEdit, None),
        ]

        for r, (label_text, widget_cls, items) in enumerate(rows):
            lbl = QLabel(label_text)
            lbl.setFont(font_body)
            grid.addWidget(lbl, r, 0)
            self._special_widgets.append(lbl)

            if widget_cls is QComboBox:
                w = widget_cls()
                w.addItems(items)
                self.controls["sheet"] = w
            else:
                w = widget_cls()
                key = "row" if label_text.startswith("Starting") else "cols"
                self.controls[key] = w

            w.setFont(font_body)
            grid.addWidget(w, r, 1)
            self._special_widgets.append(w)

        # radio buttons for column labeling options
        self.unlabeled_rb = QRadioButton("Columns not labeled")
        self.labeled_rb   = QRadioButton("Columns labeled")
        for rb in (self.unlabeled_rb, self.labeled_rb):
            rb.setFont(font_body)
            self._special_widgets.append(rb)

        group = QButtonGroup(self)
        group.addButton(self.unlabeled_rb)
        group.addButton(self.labeled_rb)
        self.unlabeled_rb.setChecked(True)

        grid.addWidget(self.unlabeled_rb, 3, 0)
        grid.addWidget(self.labeled_rb,   3, 1)

        main_vbox.addLayout(grid)

        # ok button to confirm selection and close dialog
        ok_btn = QPushButton("OK")
        ok_btn.setFont(font_title)
        ok_btn.clicked.connect(self._on_ok)
        ok_btn.setDefault(True)
        main_vbox.addWidget(ok_btn, alignment=Qt.AlignCenter)

        # hide special-case widgets until user selects special mode
        self._toggle_special(False)
        self.base_rb.toggled.connect(
            lambda checked: self._toggle_special(not checked)
        )

    def _toggle_special(self, show: bool) -> None:
        """show or hide every widget relevant to special-case mode"""
        for w in self._special_widgets:
            w.setVisible(show)
        self.adjustSize()
        
    def _on_ok(self) -> None:
        """validate special-case inputs or accept base-case directly"""
        if self.base_rb.isChecked():
            self._labeled = False
            self.accept()
            return

        cols = self.controls["cols"].text().strip()
        row  = self.controls["row"].text().strip()

        try:
            validate_special_case(cols, row)
        except InvalidExcelFormatError as exc:
            QMessageBox.warning(self, "invalid input", str(exc))
            return
        
        self._labeled = self.labeled_rb.isChecked()
        self.accept()

    def get_params(self) -> Tuple[str, str, str]:
        """
        return (sheet, starting_row, column_range, labeled_flag)

        base case: (first_sheet, "", "")
        special case: values chosen by user
        """
        if self.base_rb.isChecked():
            return self.sheets[0], "", ""
        return (
            self.controls["sheet"].currentText(),
            self.controls["row"].text().strip(),
            self.controls["cols"].text().strip(),
            self.labeled_rb.isChecked()
        )
