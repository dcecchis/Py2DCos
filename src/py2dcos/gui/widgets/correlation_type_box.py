# py2dcos/gui/widgets/correlation_type_box.py
from PyQt5.QtWidgets import QHBoxLayout, QRadioButton
from PyQt5.QtCore    import Qt
from py2dcos.config.resources import CorrType
from py2dcos.gui.widgets.base_box import BaseBox

class CorrelationTypeBox(BaseBox):
    def __init__(self, state, parent=None):
        super().__init__("Correlation Type", state, parent)

        layout = QHBoxLayout()
        self.homo = QRadioButton("Homocorrelation")
        self.hetero = QRadioButton("Heterocorrelation")
        layout.addWidget(self.homo)
        layout.addWidget(self.hetero)
        self.lay.addLayout(layout)

        # default
        (self.homo if state.corr_type is CorrType.HOMO else self.hetero).setChecked(True)

        # connect
        self.homo.toggled.connect(self._on_change)
        self.hetero.toggled.connect(self._on_change)

    def _on_change(self):
        new_val = CorrType.HOMO if self.homo.isChecked() else CorrType.HETERO
        if new_val != self.state.corr_type:
            self.state.corr_type = new_val
            self.state_changed.emit({"corr_type": new_val})
