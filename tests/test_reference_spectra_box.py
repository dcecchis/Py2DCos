# File: tests/test_reference_spectra_box.py
import pytest
from PyQt5.QtCore import Qt
from py2dcos.gui.widgets.reference_spectra_box import ReferenceSpectraBox
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.config.resources import RefSpectra
from py2dcos.datatypes import MathSettings

@pytest.fixture
def ref_box(qtbot):
    """Instantiate and expose the ReferenceSpectraBox widget."""
    box = ReferenceSpectraBox(GuiSnapshot())
    qtbot.addWidget(box)
    box.show()
    qtbot.waitExposed(box)
    return box

# -----------------------------------------------------------
# 1. Default selection matches snapshot
# -----------------------------------------------------------

def test_initial_selection(ref_box):
    snap = ref_box.snapshot
    default_ref = snap.math.ref
    assert ref_box.mean_button.isChecked() == (default_ref is RefSpectra.MEAN)
    assert ref_box.zero_button.isChecked() == (default_ref is RefSpectra.ZERO)
    assert ref_box.initial_button.isChecked() == (default_ref is RefSpectra.INITIAL)
    assert ref_box.final_button.isChecked() == (default_ref is RefSpectra.FINAL)

# -----------------------------------------------------------
# 2. update_from_snapshot syncs controls
# -----------------------------------------------------------

def test_update_from_snapshot(ref_box):
    # Change to ZERO
    new_math = ref_box.snapshot.math.update(ref=RefSpectra.ZERO)
    snap2 = ref_box.snapshot.update(math=new_math)
    ref_box.update_from_snapshot(snap2)
    assert ref_box.zero_button.isChecked()

    # Change to FINAL
    new_math2 = new_math.update(ref=RefSpectra.FINAL)
    snap3 = snap2.update(math=new_math2)
    ref_box.update_from_snapshot(snap3)
    assert ref_box.final_button.isChecked()

# -----------------------------------------------------------
# 3. state_changed emits correct MathSettings on toggle
# -----------------------------------------------------------

def _capture_math(ref_box, qtbot, element):
    with qtbot.waitSignal(ref_box.state_changed, timeout=500) as spy:
        qtbot.mouseClick(element, Qt.LeftButton)
    return spy.args[0]['math']


def test_emit_mean(ref_box, qtbot):
    math = _capture_math(ref_box, qtbot, ref_box.mean_button)
    assert isinstance(math, MathSettings)
    assert math.ref is RefSpectra.MEAN


def test_emit_zero(ref_box, qtbot):
    math = _capture_math(ref_box, qtbot, ref_box.zero_button)
    assert math.ref is RefSpectra.ZERO


def test_emit_initial(ref_box, qtbot):
    # If INITIAL is already selected, click MEAN first so a toggle occurs
    if ref_box.initial_button.isChecked():
        qtbot.mouseClick(ref_box.mean_button, Qt.LeftButton)
        qtbot.waitSignal(ref_box.state_changed, timeout=500)

    math = _capture_math(ref_box, qtbot, ref_box.initial_button)
    assert math.ref is RefSpectra.INITIAL


def test_emit_final(ref_box, qtbot):
    math = _capture_math(ref_box, qtbot, ref_box.final_button)
    assert math.ref is RefSpectra.FINAL