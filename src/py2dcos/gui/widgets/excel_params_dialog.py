"""
excel_params_dialog.py

Modal dialog for getting Excel file parameters: sheet name, start row, column range.
"""
import logging
from typing import Optional, Tuple

import pandas as pd
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout,
    QLabel, QRadioButton, QComboBox, QLineEdit,
    QButtonGroup, QPushButton, QMessageBox, QWidget
)
from PyQt5.QtGui import QFont

from py2dcos.core.validators import validate_special_case, InvalidExcelFormatError

logger = logging.getLogger(__name__)


class ExcelParamsDialog(QDialog):
    """
    Dialog to select Excel parsing options: sheet, row, and column range.

    If 'Base Case' is chosen, returns the first sheet with empty row and column.
    Otherwise validates special-case inputs via `validate_special_case`.
    """
    def __init__(self, excel_path: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.excel_path = excel_path
        self.setModal(True)

        # Attempt to read sheet names
        try:
            self.sheets = pd.ExcelFile(excel_path).sheet_names
        except Exception as e:
            logger.exception("Failed to read Excel file: %s", excel_path)
            QMessageBox.critical(self, "Excel Read Error", str(e))
            self.reject()
            return

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configure dialog widgets."""
        # Fonts
        font_title = QFont("Arial", 12, QFont.Bold)
        font_body  = QFont("Arial", 10)

        self.setWindowTitle("Excel File Options")
        layout = QVBoxLayout(self)

        # Header label
        header = QLabel("Excel File Options")
        header.setFont(font_title)
        layout.addWidget(header)

        # Base vs Special case radio buttons
        self.base_rb    = QRadioButton("Base Case (no extra spec)")
        self.special_rb = QRadioButton("Special Case (specify)")
        self.base_rb.setFont(font_body)
        self.special_rb.setFont(font_body)
        self.base_rb.setChecked(True)
        layout.addWidget(self.base_rb)
        layout.addWidget(self.special_rb)

        # Grid for special-case entries
        grid = QGridLayout()
        labels = [("Sheet Name", QComboBox, self.sheets),
                  ("Starting Row", QLineEdit, None),
                  ("Column Range", QLineEdit, None)]
        self.controls = {}
        for row, (lbl_text, widget_cls, items) in enumerate(labels):
            lbl = QLabel(lbl_text)
            lbl.setFont(font_body)
            grid.addWidget(lbl, row, 0)
            if widget_cls is QComboBox:
                cbo = widget_cls()
                cbo.setFont(font_body)
                cbo.addItems(items)
                grid.addWidget(cbo, row, 1)
                self.controls['sheet'] = cbo
            else:
                edit = widget_cls()
                edit.setFont(font_body)
                grid.addWidget(edit, row, 1)
                if lbl_text.startswith("Starting"):
                    self.controls['row'] = edit
                else:
                    self.controls['cols'] = edit
        # Column labeling options
        self.unlabeled_rb = QRadioButton("Not labeled Columns")
        self.labeled_rb   = QRadioButton("Labeled Columns")
        self.unlabeled_rb.setFont(font_body)
        self.labeled_rb.setFont(font_body)
        btn_group = QButtonGroup(self)
        btn_group.addButton(self.unlabeled_rb)
        btn_group.addButton(self.labeled_rb)
        self.unlabeled_rb.setChecked(True)
        grid.addWidget(self.unlabeled_rb, 3, 0)
        grid.addWidget(self.labeled_rb,   3, 1)
        layout.addLayout(grid)

        # Hide special-case inputs until needed
        self._toggle_special(False)
        self.base_rb.toggled.connect(lambda checked: self._toggle_special(not checked))

        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.setFont(font_title)
        ok_btn.clicked.connect(self._on_ok)
        layout.addWidget(ok_btn)

    def _toggle_special(self, show: bool) -> None:
        """Show or hide special-case input fields."""
        for widget in (*self.controls.values(), self.unlabeled_rb, self.labeled_rb):
            widget.setVisible(show)

    def _on_ok(self) -> None:
        """Validate inputs and close the dialog."""
        if self.base_rb.isChecked():
            self.accept()
            return
        cols = self.controls['cols'].text().strip()
        row  = self.controls['row'].text().strip()
        try:
            validate_special_case(cols, row)
        except InvalidExcelFormatError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return
        self.accept()

    def get_params(self) -> Tuple[str, str, str]:
        """
        Return (sheet_name, row_text, column_range).
        Base Case -> (first_sheet, "", "").
        Special Case -> selected values.
        """
        if self.base_rb.isChecked():
            return (self.sheets[0], "", "")
        return (
            self.controls['sheet'].currentText(),
            self.controls['row'].text().strip(),
            self.controls['cols'].text().strip(),
        )
