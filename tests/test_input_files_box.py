# File: tests/test_input_files_box.py
import pytest
import pytestqt.exceptions
from pathlib import Path
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.QtCore import Qt
from py2dcos.gui.widgets.input_files_box import InputFilesBox
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.types import InputFile, ExcelParams
from py2dcos.config.resources import CorrType

# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_file_dialog_and_excel(monkeypatch):
    """Patch QFileDialog.getOpenFileName and ExcelParamsDialog for tests."""
    # Default: return empty (cancel)
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *args, **kwargs: ('',''))
    # Patch ExcelParamsDialog to no-op
    from py2dcos.gui.widgets.excel_params_dialog import ExcelParamsDialog
    class DummyExcelDialog:
        def __init__(self, path, parent=None):
            self._params = ('Sheet1','1','A:C', True)
        def exec_(self):
            return QDialog.Accepted
        def get_params(self):
            return self._params
    monkeypatch.setattr('py2dcos.gui.widgets.input_files_box.ExcelParamsDialog', DummyExcelDialog)

@pytest.fixture
def input_box(qtbot):
    snap = GuiSnapshot()
    box = InputFilesBox(snap)
    qtbot.addWidget(box)
    box.show()
    qtbot.waitExposed(box)
    return box

# ---------------------------------------------------------------------------
# 1. Initial state
# ---------------------------------------------------------------------------

def test_initial_state(input_box):
    # file1 button shows default text
    assert input_box.file1_btn.text() == 'Choose your file'
    # file2 is hidden for default homo
    assert not input_box.file2_btn.isVisible()

# ---------------------------------------------------------------------------
# 2. Snapshot-driven UI
# ---------------------------------------------------------------------------

def test_apply_snapshot_shows_buttons(input_box):
    # Create dummy InputFile objects
    f1 = InputFile(path='data1.csv', extension='csv', excel_params=None)
    f2 = InputFile(path='data2.txt', extension='txt', excel_params=None)
    # Update snapshot to heterocorrelation to show file2
    new_snap = input_box.snapshot.update(corr_type=CorrType.HETERO, file1=f1, file2=f2)
    input_box.update_from_snapshot(new_snap)

    assert input_box.file1_btn.text() == Path(f1.path).name
    assert input_box.file1_btn.toolTip() == f1.path

    assert input_box.file2_btn.isVisible()
    assert input_box.file2_btn.text() == Path(f2.path).name
    assert input_box.file2_btn.toolTip() == f2.path

# ---------------------------------------------------------------------------
# 3. File selection emits state_changed for CSV
# ---------------------------------------------------------------------------

def test_csv_selection_emits_inputfile(input_box, qtbot, monkeypatch):
    # Patch getOpenFileName to return a csv path
    csv_path = 'C:/tmp/test.csv'
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *args, **kwargs: (csv_path, ''))

    with qtbot.waitSignal(input_box.state_changed, timeout=500) as spy:
        qtbot.mouseClick(input_box.file1_btn, Qt.LeftButton)
    payload = spy.args[0]
    assert 'file1' in payload
    inp: InputFile = payload['file1']
    assert inp.path == csv_path
    assert inp.extension == 'csv'
    assert inp.excel_params is None

# ---------------------------------------------------------------------------
# 4. Excel selection invokes dialog and emits ExcelParams
# ---------------------------------------------------------------------------

def test_xlsx_selection_emits_with_excel_params(input_box, qtbot, monkeypatch):
    # Patch to return .xlsx
    xlsx_path = 'C:/tmp/test.xlsx'
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *args, **kwargs: (xlsx_path, ''))

    with qtbot.waitSignal(input_box.state_changed, timeout=500) as spy:
        qtbot.mouseClick(input_box.file1_btn, Qt.LeftButton)
    payload = spy.args[0]
    assert 'file1' in payload
    inp: InputFile = payload['file1']
    assert inp.path == xlsx_path
    assert inp.extension == 'xlsx'
    assert isinstance(inp.excel_params, tuple) and len(inp.excel_params) == 4

# ---------------------------------------------------------------------------
# 5. Cancel Excel dialog does not emit
# ---------------------------------------------------------------------------

def test_xlsx_cancel_does_not_emit(input_box, qtbot, monkeypatch):
    # Patch to return .xlsx and dialog abort
    xlsx_path = 'C:/tmp/test2.xlsx'
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *args, **kwargs: (xlsx_path, ''))
    from py2dcos.gui.widgets.input_files_box import ExcelParamsDialog
    # Make exec_ return Rejected
    class AbortDialog(ExcelParamsDialog):
        def exec_(self):
            return QDialog.Rejected
    monkeypatch.setattr('py2dcos.gui.widgets.input_files_box.ExcelParamsDialog', AbortDialog)

    # No signal should fire on cancel
    with pytest.raises(pytestqt.exceptions.TimeoutError):
        with qtbot.waitSignal(input_box.state_changed, timeout=300):
            qtbot.mouseClick(input_box.file1_btn, Qt.LeftButton)