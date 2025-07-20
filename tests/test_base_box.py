import pytest
from PyQt5.QtWidgets import QSlider, QApplication
from py2dcos.gui.widgets.base_box import BaseBox
from py2dcos.gui.state.gui_snapshot import GuiSnapshot

class DummyBox(BaseBox):
    """Minimal concrete subclass so we can instantiate BaseBox."""
    def __init__(self, snapshot):
        super().__init__("Dummy", snapshot)
        # add one child slider to test signal blocking
        self.slider = QSlider()
        self.lay.addWidget(self.slider)

@pytest.fixture
def dummy_box(qtbot):
    """Create and show a DummyBox for testing."""
    box = DummyBox(GuiSnapshot())
    qtbot.addWidget(box)
    box.show()
    qtbot.waitExposed(box)
    return box

def test_update_from_snapshot(dummy_box):
    # initial snapshot
    old_snap = dummy_box.snapshot
    assert isinstance(old_snap, GuiSnapshot)

    # create a new snapshot with a dummy change
    new_snap = old_snap.update(show_3d=not old_snap.show_3d)
    # apply it
    dummy_box.update_from_snapshot(new_snap)
    # BaseBox.update_from_snapshot should store the new snapshot
    assert dummy_box.snapshot is new_snap

def test_block_signals_prevents_slider_signal(dummy_box, qtbot):
    calls = []

    # connect the slider's valueChanged to record calls
    dummy_box.slider.valueChanged.connect(lambda v: calls.append(v))

    # outside block_signals: setting value emits signal
    dummy_box.slider.setValue(5)
    assert calls == [5]

    calls.clear()

    # inside block_signals: no signal should fire
    with dummy_box.block_signals(dummy_box.slider):
        dummy_box.slider.setValue(7)
    assert calls == []

    # after block_signals context, signals are unblocked again
    dummy_box.slider.setValue(9)
    assert calls == [9]
