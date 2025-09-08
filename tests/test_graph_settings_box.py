# File: tests/test_graph_settings_box.py
import pytest
from PyQt5.QtCore import Qt
from py2dcos.gui.widgets.graph_settings_box import GraphSettingsBox
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.datatypes import PlotSettings


@pytest.fixture
def graph_box(qtbot):
    box = GraphSettingsBox(GuiSnapshot())
    qtbot.addWidget(box)
    box.show()
    qtbot.waitExposed(box)
    return box


# -----------------------------------------------------------
# 1. Defaults match snapshot
# -----------------------------------------------------------

def test_defaults(graph_box):
    p = graph_box.snapshot.plot
    assert graph_box.num_slider.value() == p.num_contours
    assert graph_box.locator_box.currentText() == p.locator
    assert graph_box.color_map_box.currentText() == p.color_map
    assert graph_box.cl_color_box.currentText() == p.contour_line_color
    assert graph_box.cmap_int_slider.value() == int(p.color_map_intensity * 100)
    assert graph_box.cl_alpha_slider.value() == int(p.contour_line_alpha * 100)


# -----------------------------------------------------------
# 2. Update from snapshot
# -----------------------------------------------------------

def test_update_from_snapshot(graph_box):
    new_plot = graph_box.snapshot.plot.update(
        num_contours=8,
        locator="log",
        color_map="coolwarm",
        contour_line_color="red",
        color_map_intensity=0.5,
        contour_line_alpha=0.3,
    )
    new_snap = graph_box.snapshot.update(plot=new_plot)
    graph_box.update_from_snapshot(new_snap)

    assert graph_box.num_slider.value() == 8
    assert graph_box.locator_box.currentText() == "log"
    assert graph_box.color_map_box.currentText() == "coolwarm"
    assert graph_box.cl_color_box.currentText() == "red"
    assert graph_box.cmap_int_slider.value() == 50
    assert graph_box.cl_alpha_slider.value() == 30


# -----------------------------------------------------------
# 3. Emitted PlotSettings when user interacts
# -----------------------------------------------------------

def _capture_state_changed(graph_box, qtbot, trigger):
    with qtbot.waitSignal(graph_box.state_changed, timeout=500) as spy:
        trigger()
    return spy.args[0]["plot"]


def test_num_slider_emits(graph_box, qtbot):
    plot = _capture_state_changed(
        graph_box,
        qtbot,
        lambda: (
            graph_box.num_slider.setValue(7),
            graph_box.num_slider.sliderReleased.emit(),
        ),
    )
    assert plot.num_contours == 7


def test_locator_combo_emits(graph_box, qtbot):
    # Ensure locator box actually changes *and* activation signal fires
    idx = graph_box.locator_box.findText("log")

    def trigger():
        graph_box.locator_box.setCurrentIndex(idx)          # change selection
        # Manually emit activated because setCurrentIndex alone doesn't emit it
        graph_box.locator_box.activated[str].emit("log")  # this calls _emit_plot

    plot = _capture_state_changed(graph_box, qtbot, trigger)
    assert plot.locator == "log"


def test_color_intensity_slider_emits(graph_box, qtbot):
    plot = _capture_state_changed(
        graph_box,
        qtbot,
        lambda: (
            graph_box.cmap_int_slider.setValue(70),
            graph_box.cmap_int_slider.sliderReleased.emit(),
        ),
    )
    assert plot.color_map_intensity == 0.70
