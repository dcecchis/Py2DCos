# py2dcos/gui/widgets/correlation_type_box.py

from PyQt5.QtWidgets import QHBoxLayout, QRadioButton
from PyQt5.QtCore    import pyqtSignal

from py2dcos.config.resources import CorrType
from .base_box import BaseBox

class CorrelationTypeBox(BaseBox):
    """
    Section to choose between homocorrelation and heterocorrelation.

    Emits state_changed with:
      - 'corr_type': CorrType enum
    """
    state_changed = pyqtSignal(dict)

    def __init__(self, state, parent=None):
        super().__init__("Correlation Type", state, parent)

        layout = QHBoxLayout()
        self.homo   = QRadioButton("Homocorrelation")
        self.hetero = QRadioButton("Heterocorrelation")
        self._controls = [self.homo, self.hetero]
        layout.addWidget(self.homo)
        layout.addWidget(self.hetero)
        self.lay.addLayout(layout)

        # Set default based on initial state
        if state.corr_type is CorrType.HOMO:
            self.homo.setChecked(True)
        else:
            self.hetero.setChecked(True)

        # Connect signals
        self.homo.toggled.connect(self._on_change)
        self.hetero.toggled.connect(self._on_change)
    
        
    
    def update_from_state(self, state):
        with self.block_signals(*self._controls):
            if state.corr_type is CorrType.HOMO:
                self.homo  .setChecked(True)
            else:
                self.hetero.setChecked(True)

    def _on_change(self, checked: bool):
        if not checked:
            return

        new_val = CorrType.HOMO if self.homo.isChecked() else CorrType.HETERO
        # Emit only on actual change
        self.state_changed.emit({"corr_type": new_val})
