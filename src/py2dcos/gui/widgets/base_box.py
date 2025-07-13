from contextlib import contextmanager
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout
from PyQt5.QtCore    import pyqtSignal, QSignalBlocker

class BaseBox(QGroupBox):
    """
    Base class for collapsible GUI sections.

    Stores an initial state snapshot and provides a `state_changed`
    signal carrying a dict of field updates.
    """
    state_changed = pyqtSignal(dict)

    def __init__(self, title: str, state, parent=None):
        """
        :param title: Section header text
        :param state: Initial GuiState for setting up controls
        :param parent: Optional parent widget
        """
        super().__init__(title, parent)
        # store state snapshot for initializing controls; do not mutate
        self.state = state

        # Consistent styling for all input controls
        self.setStyleSheet("""
            QGroupBox { font: bold 12pt Arial; }
            QLabel    { font: 10pt Arial; }
            QComboBox { font: 10pt Arial; }
            QSlider   { font: 10pt Arial; }
            QCheckBox { font: 10pt Arial; }
            QRadioButton { font: 10pt Arial; }
            QPushButton { font: 10pt Arial; }
        """
        )
        self.setFlat(True)

        # Layout container for child widgets
        self.lay = QVBoxLayout(self)

    def update_from_state(self, state):
        """
        Override in subclasses to refresh UI controls
        based on the new GuiState.
        """
        pass

    @contextmanager
    def block_signals(self, *widgets):
        """
        Context-manager that blocks signals on the given widgets
        for the duration of a with-block.
        """
        blockers = [QSignalBlocker(w) for w in widgets]
        try:
            yield
        finally:
            # QSignalBlockers auto-destroy here, re-enabling signals
            del blockers
