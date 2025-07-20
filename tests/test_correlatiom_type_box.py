# File: tests/test_correlation_type_box.py
import pytest
from py2dcos.gui.widgets.correlation_type_box import CorrelationTypeBox
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.config.resources import CorrType

@pytest.fixture
def corr_box(qtbot):
    """Create and expose a CorrelationTypeBox for testing."""
    box = CorrelationTypeBox(GuiSnapshot())
    qtbot.addWidget(box)
    box.show()
    qtbot.waitExposed(box)
    return box


def test_initial_selection(corr_box):
    # Default GuiSnapshot.corr_type is HOMO
    assert corr_box.homo.isChecked()
    assert not corr_box.hetero.isChecked()


def test_update_from_snapshot(corr_box):
    # Flip to HETERO via snapshot.update
    new_snap = corr_box.snapshot.update(corr_type=CorrType.HETERO)
    corr_box.update_from_snapshot(new_snap)
    assert corr_box.hetero.isChecked()
    assert not corr_box.homo.isChecked()


def test_emit_state_changed_to_hetero(corr_box, qtbot):
    # Toggling hetero should emit state_changed with CorrType.HETERO
    with qtbot.waitSignal(corr_box.state_changed, timeout=500) as caught:
        corr_box.hetero.setChecked(True)
    payload = caught.args[0]
    assert payload == {"corr_type": CorrType.HETERO}


def test_emit_state_changed_to_homo(corr_box, qtbot):
    # Switch to HETERO first so HOMO toggle will fire
    corr_box.hetero.setChecked(True)
    # Then toggle back to HOMO and capture signal
    with qtbot.waitSignal(corr_box.state_changed, timeout=500) as caught:
        corr_box.homo.setChecked(True)
    payload = caught.args[0]
    assert payload == {"corr_type": CorrType.HOMO}
