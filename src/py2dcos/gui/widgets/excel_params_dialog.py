import pandas as pd
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout,
    QLabel, QRadioButton, QComboBox, QLineEdit,
    QButtonGroup, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont
from py2dcos.core.validators import validate_special_case, InvalidExcelFormatError

class ExcelParamsDialog(QDialog):
    """
    Modal dialog for Excel special-case parameters: sheet, start row, column range.
    """
    def __init__(self, excel_path: str, parent=None):
        super().__init__(parent)
        self.excel_path = excel_path
        # load sheet names from the file
        self.sheets = pd.ExcelFile(excel_path).sheet_names
        self._setup_ui()

    def _setup_ui(self):
        # Fonts
        font_title = QFont("Arial", 12, QFont.Bold)
        font = QFont("Arial", 10)

        self.setWindowTitle("Excel File Options")
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Excel File Options")
        header.setFont(font_title)
        layout.addWidget(header)

        # Base vs Special case
        self.base_rb = QRadioButton("Base Case (no extra spec)")
        self.base_rb.setFont(font)
        self.base_rb.setChecked(True)
        layout.addWidget(self.base_rb)

        self.special_rb = QRadioButton("Special Case (specify)")
        self.special_rb.setFont(font)
        layout.addWidget(self.special_rb)

        # Grid for special-case inputs
        grid = QGridLayout()
        # Labels
        self.sheet_lbl = QLabel("Sheet Name"); self.sheet_lbl.setFont(font)
        self.row_lbl   = QLabel("Starting Row"); self.row_lbl.setFont(font)
        self.col_lbl   = QLabel("Column Range"); self.col_lbl.setFont(font)
        # Controls
        self.sheet_combo = QComboBox(); self.sheet_combo.setFont(font)
        self.sheet_combo.addItems(self.sheets)
        self.row_edit    = QLineEdit();    self.row_edit.setFont(font)
        self.col_edit    = QLineEdit();    self.col_edit.setFont(font)
        # Labeled vs unlabeled columns
        self.unlabeled_rb = QRadioButton("Not labeled Columns"); self.unlabeled_rb.setFont(font)
        self.labeled_rb   = QRadioButton("Labeled Columns");     self.labeled_rb.setFont(font)
        btn_group = QButtonGroup(self)
        btn_group.addButton(self.unlabeled_rb)
        btn_group.addButton(self.labeled_rb)
        self.unlabeled_rb.setChecked(True)

        grid.addWidget(self.sheet_lbl, 0, 0)
        grid.addWidget(self.sheet_combo, 0, 1)
        grid.addWidget(self.row_lbl,   1, 0)
        grid.addWidget(self.row_edit,  1, 1)
        grid.addWidget(self.col_lbl,   2, 0)
        grid.addWidget(self.col_edit,  2, 1)
        grid.addWidget(self.unlabeled_rb, 3, 0)
        grid.addWidget(self.labeled_rb,   3, 1)
        layout.addLayout(grid)

        # Hide special-case fields initially
        self._toggle_special(False)
        self.base_rb.toggled.connect(lambda checked: self._toggle_special(not checked))

        # OK button
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setFont(font_title)
        self.ok_btn.clicked.connect(self._on_ok)
        layout.addWidget(self.ok_btn)

    def _toggle_special(self, show: bool):
        # Show/hide all the grid widgets for special case
        for w in (
            self.sheet_lbl, self.sheet_combo,
            self.row_lbl,   self.row_edit,
            self.col_lbl,   self.col_edit,
            self.unlabeled_rb, self.labeled_rb
        ):
            w.setVisible(show)

    def _on_ok(self):
        # If base case, accept immediately
        if self.base_rb.isChecked():
            self.accept()
            return
        # Otherwise validate the user inputs
        cols = self.col_edit.text().strip()
        row  = self.row_edit.text().strip()
        try:
            validate_special_case(cols, row)
        except InvalidExcelFormatError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return
        self.accept()

    def get_params(self) -> tuple[str, str, str]:
        """
        Returns a tuple (sheet_name, row_text, column_range).
        For Base Case, returns (first_sheet, "", "").
        """
        if self.base_rb.isChecked():
            return (self.sheets[0], "", "")
        return (
            self.sheet_combo.currentText(),
            self.row_edit.text().strip(),
            self.col_edit.text().strip()
        )
