from PyQt5.QtWidgets import QHBoxLayout, QRadioButton
from PyQt5.QtCore    import pyqtSignal

from py2dcos.config.resources import CorrType
from .base_box import BaseBox

class CorrelationTypeBox(BaseBox):
    """
    section to choose between homocorrelation and heterocorrelation.

    emits state_changed with:
      - 'corr_type': corrtype enum
    """
    state_changed = pyqtSignal(dict)

    def __init__(self, state, parent=None):
        super().__init__("Correlation Type", state, parent)

        # use a horizontal layout so options sit side by side
        layout = QHBoxLayout()
        self.homo = QRadioButton("Homocorrelation")
        self.hetero = QRadioButton("Heterocorrelation")
        self._controls = [self.homo, self.hetero]

        layout.addWidget(self.homo)
        layout.addWidget(self.hetero)
        self.lay.addLayout(layout)

        # initialize selection to reflect the current state
        if state.corr_type is CorrType.HOMO:
            self.homo.setChecked(True)
        else:
            self.hetero.setChecked(True)

        # listen for toggles and handle changes centrally
        self.homo.toggled.connect(self._on_change)
        self.hetero.toggled.connect(self._on_change)

    def update_from_state(self, state):
        # temporarily block signals to avoid feedback loops when mirroring state
        with self.block_signals(*self._controls):
            if state.corr_type is CorrType.HOMO:
                self.homo.setChecked(True)
            else:
                self.hetero.setChecked(True)

    def _on_change(self, checked: bool):
        # ignore off-signals to only react on activation
        if not checked:
            return

        # decide new enum value based on which button is active
        new_val = CorrType.HOMO if self.homo.isChecked() else CorrType.HETERO
        # emit only the changed field for downstream handling
        self.state_changed.emit({"corr_type": new_val})
