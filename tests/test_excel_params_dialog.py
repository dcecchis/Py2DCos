# File: tests/test_excel_params_dialog.py
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from py2dcos.gui.widgets.excel_params_dialog import ExcelParamsDialog

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

class DummyExcelFile:
    """Stub object to replace pandas.ExcelFile."""
    def __init__(self, path):
        self.sheet_names = ["Sheet1", "Second", "Third"]

@pytest.fixture(autouse=True)
def patch_pandas(monkeypatch):
    """Patch pandas.ExcelFile to avoid real file IO."""
    import pandas as pd
    monkeypatch.setattr(pd, "ExcelFile", DummyExcelFile)

@pytest.fixture
def dialog(qtbot):
    dlg = ExcelParamsDialog("dummy.xlsx")
    qtbot.addWidget(dlg)
    dlg.show()
    qtbot.waitExposed(dlg)
    return dlg

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_base_case_accepts_and_returns_defaults(dialog, qtbot):
    # Base radio is checked by default.
    qtbot.keyClick(dialog, Qt.Key_Return)  # triggers default OK button
    qtbot.waitUntil(lambda: dialog.result() == dialog.Accepted, timeout=500)
    assert dialog.result() == dialog.Accepted
    params = dialog.get_params()
    # Should be 3‑tuple of (first_sheet, '', '')
    assert params == ("Sheet1", "", "")


def test_special_case_valid_inputs(dialog, qtbot):
    # Select special mode
    dialog.special_rb.setChecked(True)
    # Fill in controls
    dialog.controls["sheet"].setCurrentText("Second")
    dialog.controls["row"].setText("2")
    dialog.controls["cols"].setText("A:C")
    dialog.labeled_rb.setChecked(True)

    # Click OK
    QTest.keyClick(dialog, Qt.Key_Return)
    assert dialog.result() == dialog.Accepted

    sheet, row, cols, labeled = dialog.get_params()
    assert (sheet, row, cols, labeled) == ("Second", "2", "A:C", True)


def test_special_case_missing_inputs_rejected(dialog, qtbot, monkeypatch):
    # Override validator to raise
    from py2dcos.core import validators as val_mod
    monkeypatch.setattr(val_mod, "validate_special_case", lambda c, r: (_ for _ in ()).throw(val_mod.InvalidExcelFormatError("bad")))

    dialog.special_rb.setChecked(True)
    dialog.controls["row"].setText("")
    dialog.controls["cols"].setText("")

    # Click OK
    QTest.keyClick(dialog, Qt.Key_Return)
    # Dialog should remain open (Rejected not set)
    assert dialog.result() == 0  # 0 = QDialog.NoResult yet
