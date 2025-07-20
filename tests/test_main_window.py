# File: tests/test_main_window.py
import pytest
from py2dcos.gui.main_window import MainWindow

@pytest.fixture
def main_window(qtbot):
    """Create, show, and expose a MainWindow."""
    mw = MainWindow()
    qtbot.addWidget(mw)
    mw.show()
    qtbot.waitExposed(mw)    # ensure window is painted
    return mw

def test_fonts(main_window):
    title_font = main_window.get_font_title()
    assert title_font.family() == "arial"
    assert title_font.pointSize() == 12
    assert title_font.bold()

    text_font = main_window.get_font_text()
    assert text_font.family() == "arial"
    assert text_font.pointSize() == 10
    assert not text_font.bold()

def test_set_status_shows_label(main_window, qtbot):
    mw = main_window
    mw._set_status("testing 123")

    # wait until the label actually becomes visible
    qtbot.waitUntil(lambda: mw.status_label.isVisible(), timeout=500)

    assert mw.status_label.text() == "testing 123"
    assert mw.status_label.isVisible()

def test_show_and_hide_busy(main_window):
    mw = main_window

    mw._show_busy()
    assert not mw.plot_button.isEnabled()
    assert not mw.btn_3d.isEnabled()
    assert mw.status_label.text() == "Re-calculating…"

    mw._hide_busy()
    assert mw.plot_button.isEnabled()
    assert mw.btn_3d.isEnabled()
    assert mw.status_label.text() == "Ready"

def test_toggle_3d_view(main_window):
    mw = main_window

    # initial state: 2D visible, button text "Show 3D plot"
    assert mw.canvas.isVisible()
    assert not mw.webview.isVisible()
    assert mw.btn_3d.text() == "Show 3D plot"

    # switch to 3D
    mw._on_widget_delta({"show_3d": True})
    assert not mw.canvas.isVisible()
    assert mw.webview.isVisible()
    assert mw.btn_3d.isChecked()
    assert mw.btn_3d.text() == "Show 2D"

    # switch back to 2D
    mw._on_widget_delta({"show_3d": False})
    assert mw.canvas.isVisible()
    assert not mw.webview.isVisible()
    assert not mw.btn_3d.isChecked()
    assert mw.btn_3d.text() == "Show 3D"

def test_force_plot_does_not_toggle(main_window):
    mw = main_window

    # manually go into 3D
    mw._on_widget_delta({"show_3d": True})
    assert mw.webview.isVisible()

    # force a plot (force=True) without changing show_3d
    mw._on_widget_delta({}, force=True)
    assert mw.webview.isVisible()
    assert not mw.canvas.isVisible()
