from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QPushButton
import logging

from .excel_params_dialog import ExcelParamsDialog
from py2dcos.config.resources import GuiState
from .base_box import BaseBox


class InputFilesBox(BaseBox):
    """
    A collapsible section for selecting one or two input files.

    Emits state_changed with keys:
      - 'filename1': (path, fmt)
      - 'format1': fmt
      - 'excel_params1': (sheet, row, cols) if fmt is 'xlsx'
      - 'filename2', 'format2', 'excel_params2' similarly for the second file
    """
    def __init__(self, state: GuiState, parent=None):
        super().__init__("Input", state, parent)

        # File 1 button
        self.file1_button = QPushButton("Choose your file")
        self.file1_button.setMinimumSize(250, 30)
        self.lay.addWidget(self.file1_button)

        # File 2 button (hidden by default)
        self.file2_button = QPushButton("Choose your file")
        self.file2_button.setMinimumSize(250, 30)
        self.file2_button.hide()
        self.lay.addWidget(self.file2_button)

        # Connect signals
        self.file1_button.clicked.connect(self._choose_file1)
        self.file2_button.clicked.connect(self._choose_file2)

    def _choose_file1(self):
        try:
            path, _ = QFileDialog.getOpenFileName(
                self, "Open File", "",
                "All Files (*);;Excel files (*.xlsx);;CSV files (*.csv);;TXT files (*.txt)"
            )
            if not path:
                return
            name = path.rsplit('/', 1)[-1]
            fmt = name.rsplit('.', 1)[-1].lower() if '.' in name else ''

            # Excel file: get sheet/row/cols params
            if fmt == 'xlsx':
                dlg = ExcelParamsDialog(path, self)
                if dlg.exec_() != QDialog.Accepted:
                    return
                sheet, row, cols = dlg.get_params()
                

            self.state.filename1 = (path, fmt)
            self.state.format1 = fmt

            payload = {
                'filename1': (path, fmt),
                'format1':   fmt,
            }

            if fmt == "xlsx":
                payload["excel_params1"] = (sheet,row,cols)

            # Update UI
            self.file1_button.setText(name)
            # Notify listeners
            self.state_changed.emit(payload)

        except Exception as e:
            logging.exception("Error selecting file1")
            QMessageBox.critical(self, "Error Loading File", str(e))

    def _choose_file2(self):
        try:
            path, _ = QFileDialog.getOpenFileName(
                self, "Open File", "",
                "All Files (*);;Excel files (*.xlsx);;CSV files (*.csv);;TXT files (*.txt)"
            )
            if not path:
                return
            name = path.rsplit('/', 1)[-1]
            fmt = name.rsplit('.', 1)[-1].lower() if '.' in name else ''

            # Excel file: get sheet/row/cols params
            if fmt == 'xlsx':
                dlg = ExcelParamsDialog(path, self)
                if dlg.exec_() != QDialog.Accepted:
                    return
                sheet, row, cols = dlg.get_params()
                

            self.state.filename2 = (path, fmt)
            self.state.format2 = fmt

            payload = {
                'filename2': (path, fmt),
                'format2':   fmt,
            }

            if fmt == "xlsx":
                payload["excel_params2"] = (sheet,row,cols)

            self.file2_button.setText(name)
            self.state_changed.emit(payload)

        except Exception as e:
            logging.exception("Error selecting file2")
            QMessageBox.critical(self, "Error Loading File", str(e))
