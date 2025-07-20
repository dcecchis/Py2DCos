# File: tests/conftest.py
import pytest
from PyQt5.QtCore import QObject, pyqtSignal
import py2dcos.gui.main_window as mw_mod

# ── DummyController ─────────────────────────────────────────────────────────
class DummyController(QObject):
    busy         = pyqtSignal()
    ready        = pyqtSignal()
    fig2d_ready  = pyqtSignal(object)
    fig3d_ready  = pyqtSignal(object)
    error        = pyqtSignal(str)
    status_text  = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.parent_figure = None

    def update_snapshot(self, snapshot, force=False):
        # no-op
        pass

# ── fixtures ────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def patch_controller(monkeypatch):
    """
    Replace the real AppController with our DummyController
    so MainWindow.__init__ never spins up real plots/math.
    """
    monkeypatch.setattr(mw_mod, "AppController", DummyController)

# pytest-qt provides a `qapp` fixture; no need to re-declare QApplication here.
