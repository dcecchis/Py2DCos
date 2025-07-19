from contextlib import contextmanager
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QSignalBlocker


class BaseBox(QGroupBox):
    # base class for collapsible gui sections; captures initial state and notifies on changes
    state_changed = pyqtSignal(dict)

    def __init__(self, title: str, snapshot: GuiSnapshot, parent=None):
        # initialize the group box with a title and keep a reference to gui state for control setup
        super().__init__(title, parent)
        self.snapshot = snapshot

        # apply a consistent font style across all child widgets for uniform appearance
        self.setStyleSheet("""
            QGroupBox { font: bold 12pt Arial; }
            QLabel    { font: 10pt Arial; }
            QComboBox { font: 10pt Arial; }
            QSlider   { font: 10pt Arial; }
            QCheckBox { font: 10pt Arial; }
            QRadioButton { font: 10pt Arial; }
            QPushButton { font: 10pt Arial; }
        """)
        # remove the groupbox border to integrate cleanly into the panel
        self.setFlat(True)

        # create a vertical layout to stack child controls in order
        self.lay = QVBoxLayout(self)

    def update_from_snapshot(self, snap):
        # intended for subclasses: refresh control values to reflect the new gui state
        self.snapshot = snap

    @contextmanager
    def block_signals(self, *widgets):
        # temporarily block signals on widgets to prevent recursive updates when setting values
        blockers = [QSignalBlocker(w) for w in widgets]
        try:
            yield
        finally:
            # deleting blockers re-enables signals automatically
            del blockers
