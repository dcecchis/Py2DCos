from PyQt5.QtWidgets import QHBoxLayout, QRadioButton
from PyQt5.QtCore    import pyqtSignal
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.config.resources import CorrType
from .base_box import BaseBox

class CorrelationTypeBox(BaseBox):
    """
    section to choose between homocorrelation and heterocorrelation.

    emits state_changed with:
      - 'corr_type': corrtype enum
    """
    state_changed = pyqtSignal(dict)

    def __init__(self, snapshot: GuiSnapshot, parent=None):
        super().__init__("Correlation Type", snapshot, parent)

        # use a horizontal layout so options sit side by side
        layout = QHBoxLayout()
        self.homo = QRadioButton("Homocorrelation")
        self.hetero = QRadioButton("Heterocorrelation")
        self._controls = [self.homo, self.hetero]

        layout.addWidget(self.homo)
        layout.addWidget(self.hetero)
        self.lay.addLayout(layout)

        # mirror the snapshot once
        self._apply_snapshot(snapshot)

        # listen for toggles and handle changes centrally
        self.homo.toggled.connect(self._emit_change)
        self.hetero.toggled.connect(self._emit_change)

    def _apply_snapshot(self, snap: GuiSnapshot):
        # initialize selection to reflect the current state
        if snap.corr_type is CorrType.HOMO:
            self.homo.setChecked(True)
        else:
            self.hetero.setChecked(True)

    def update_from_snapshot(self, snap: GuiSnapshot):
        # temporarily block signals to avoid feedback loops when mirroring state
        super().update_from_snapshot(snap)
        with self.block_signals(*self._controls):
            self._apply_snapshot(snap)

    def _emit_change(self, checked: bool):
        # ignore off-signals to only react on activation
        if not checked:
            return
        
        # decide new enum value based on which button is active
        new_val = CorrType.HOMO if self.homo.isChecked() else CorrType.HETERO
        # emit only the changed field for downstream handling
        self.state_changed.emit({"corr_type": new_val})
