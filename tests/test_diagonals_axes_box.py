# File: tests/test_diagonals_axes_box.py
import pytest
from py2dcos.gui.widgets.diagonals_axes_box import DiagonalsAxesBox
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.config.resources import Diagonal, AxisDirection
from py2dcos.datatypes import PlotSettings

@pytest.fixture
def diag_box(qtbot):
    box = DiagonalsAxesBox(GuiSnapshot())
    qtbot.addWidget(box)
    box.show()
    qtbot.waitExposed(box)
    return box

# -------------------------------
# 1. Initial state sync
# -------------------------------

def test_initial_state_matches_snapshot(diag_box):
    snap = diag_box.snapshot
    # Sync diag
    assert diag_box.sync_main.isChecked() == (snap.plot.sync_diag is Diagonal.MAIN)
    assert diag_box.sync_anti.isChecked() == (snap.plot.sync_diag is Diagonal.ANTI)
    # Async diag
    assert diag_box.async_main.isChecked() == (snap.plot.async_diag is Diagonal.MAIN)
    assert diag_box.async_anti.isChecked() == (snap.plot.async_diag is Diagonal.ANTI)
    # X‑axis direction
    assert diag_box.x_incr.isChecked() == (snap.plot.x_axis is AxisDirection.INCREASING)
    assert diag_box.x_decr.isChecked() == (snap.plot.x_axis is AxisDirection.DECREASING)

# -------------------------------
# 2. update_from_snapshot syncs UI
# -------------------------------

def test_update_from_snapshot(diag_box):
    new_plot = diag_box.snapshot.plot.update(
        sync_diag=Diagonal.ANTI,
        async_diag=Diagonal.ANTI,
        x_axis=AxisDirection.DECREASING,
    )
    new_snap = diag_box.snapshot.update(plot=new_plot)
    diag_box.update_from_snapshot(new_snap)

    assert diag_box.sync_anti.isChecked()
    assert diag_box.async_anti.isChecked()
    assert diag_box.x_decr.isChecked()

# -------------------------------
# 3. state_changed emits correct PlotSettings
# -------------------------------

def _assert_payload(payload, sync_d, async_d, x_dir):
    assert 'plot' in payload
    ps: PlotSettings = payload['plot']
    assert ps.sync_diag is sync_d
    assert ps.async_diag is async_d
    assert ps.x_axis is x_dir


def test_emit_plot_signal(diag_box, qtbot):
    # 1) toggle sync diagonal to ANTI
    with qtbot.waitSignal(diag_box.state_changed, timeout=500) as spy1:
        diag_box.sync_anti.setChecked(True)
    _assert_payload(spy1.args[0], Diagonal.ANTI, diag_box.snapshot.plot.async_diag, diag_box.snapshot.plot.x_axis)

    # 2) toggle async diagonal to ANTI (if not already)
    if not diag_box.async_anti.isChecked():
        with qtbot.waitSignal(diag_box.state_changed, timeout=500) as spy2:
            diag_box.async_anti.setChecked(True)
        _assert_payload(spy2.args[0], Diagonal.ANTI, Diagonal.ANTI, diag_box.snapshot.plot.x_axis)

    # 3) ensure we actually change X‑axis toggle so a signal fires
    # First, move to INCREASING (if not already) then back to DECREASING
    if not diag_box.x_incr.isChecked():
        diag_box.x_incr.setChecked(True)
    with qtbot.waitSignal(diag_box.state_changed, timeout=500) as spy3:
        diag_box.x_decr.setChecked(True)
    _assert_payload(spy3.args[0], Diagonal.ANTI, Diagonal.ANTI, AxisDirection.DECREASING)
