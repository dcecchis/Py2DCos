# tests/test_shown_graph_box.py
# -*- coding: utf-8 -*-
"""
Assumptions:
- GuiSnapshot can be any object with a .plot attribute.
- PlotSettings(shown_graph, peaks) is sufficient to drive the widget.
- BaseBox __init__ and update_from_snapshot only rely on self.snapshot and do not require other GuiSnapshot fields.
- state_changed emits a single dict argument, not wrapped in a list/tuple.
"""
import pytest
from PyQt5.QtCore import Qt
from py2dcos.gui.widgets.shown_graph_box import ShownGraphBox
from py2dcos.config.resources import ShownGraph, PeaksSigns
from py2dcos.types import PlotSettings

def make_snapshot(shown_graph, peaks):
    """Helper to create a dummy snapshot with the given plot settings."""
    class DummySnap:
        pass
    snap = DummySnap()
    snap.plot = PlotSettings(shown_graph=shown_graph, peaks=peaks)
    return snap

@pytest.fixture
def box(qtbot):
    """Instantiate the widget with default SYNC/POSITIVE state."""
    snap = make_snapshot(ShownGraph.SYNC, PeaksSigns.POSITIVE)
    widget = ShownGraphBox(snap)
    qtbot.addWidget(widget)
    widget.show()  # ensure layouts are applied
    return widget

def test_default_state_reflects_snapshot(box):
    # initial state should mirror the snapshot (SYNC + POSITIVE)
    assert box.sync_graph.isChecked()
    assert not box.async_graph.isChecked()
    assert not box.both_graph.isChecked()
    assert box.positive.isChecked()
    assert not box.negative.isChecked()
    assert not box.all_signs.isChecked()

def test_update_from_snapshot_changes_buttons(box):
    # changing snapshot to ASYNC/NEGATIVE should update UI without emitting signals
    new_snap = make_snapshot(ShownGraph.ASYNC, PeaksSigns.NEGATIVE)
    box.update_from_snapshot(new_snap)
    assert not box.sync_graph.isChecked()
    assert box.async_graph.isChecked()
    assert not box.both_graph.isChecked()
    assert not box.positive.isChecked()
    assert box.negative.isChecked()
    assert not box.all_signs.isChecked()

def test_graph_radio_emits_state_changed(qtbot, box):
    # programmatically setting Async should emit state_changed with updated shown_graph
    with qtbot.waitSignal(box.state_changed, timeout=500) as caught:
        box.async_graph.setChecked(True)
    payload = caught.args[0]
    new_plot = payload["plot"]
    assert isinstance(new_plot, PlotSettings)
    assert new_plot.shown_graph == ShownGraph.ASYNC
    # peaks should remain unchanged
    assert new_plot.peaks == PeaksSigns.POSITIVE

def test_peaks_radio_emits_state_changed(qtbot, box):
    # programmatically setting Negatives should emit state_changed with updated peaks
    with qtbot.waitSignal(box.state_changed, timeout=500) as caught:
        box.negative.setChecked(True)
    payload = caught.args[0]
    new_plot = payload["plot"]
    assert isinstance(new_plot, PlotSettings)
    assert new_plot.peaks == PeaksSigns.NEGATIVE
    # shown_graph should remain unchanged
    assert new_plot.shown_graph == ShownGraph.SYNC

def test_both_and_all_emit_correctly(qtbot, box):
    # change to BOTH graph
    with qtbot.waitSignal(box.state_changed, timeout=500) as c1:
        box.both_graph.setChecked(True)
    p1 = c1.args[0]["plot"]
    assert p1.shown_graph == ShownGraph.BOTH
    # then change to ALL peaks
    with qtbot.waitSignal(box.state_changed, timeout=500) as c2:
        box.all_signs.setChecked(True)
    p2 = c2.args[0]["plot"]
    assert p2.peaks == PeaksSigns.ALL
