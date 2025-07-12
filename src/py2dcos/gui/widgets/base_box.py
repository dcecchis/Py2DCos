from PyQt5.QtWidgets import QGroupBox, QVBoxLayout
from PyQt5.QtCore    import pyqtSignal
from py2dcos.config.resources import GuiState   # dataclass

class BaseBox(QGroupBox):
    state_changed = pyqtSignal(dict)   # emits {"attr": value, ...}

    def __init__(self, title: str, state: GuiState, parent=None):
        super().__init__(title, parent)
        self.state = state
        self.setStyleSheet("""
            QGroupBox { font: bold 12pt Arial; }
            QLabel    { font: 10pt Arial; }
            QComboBox { font: 10pt Arial; }
            QSlider   { font: 10pt Arial; }
            QCheckBox { font: 10pt Arial; }
            QRadioButton { font: 10pt Arial; }
            QPushButton { font: 10pt Arial; }
        """)

        self.setFlat(True)
        self.lay = QVBoxLayout(self)
