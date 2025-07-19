from PyQt5.QtWidgets import QRadioButton, QGridLayout
from PyQt5.QtCore    import pyqtSignal, Qt
from py2dcos.config.resources import RefSpectra
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.types             import MathSettings
from .base_box import BaseBox

class ReferenceSpectraBox(BaseBox):
    """
    a section for choosing the reference spectra method.

    emits state_changed with:
      - 'ref_spectra': refspectra enum
    """
    # notify main window when user picks a different reference method
    state_changed = pyqtSignal(dict)

    def __init__(self, snapshot: GuiSnapshot, parent=None):
        super().__init__("Reference Spectra", snapshot, parent)

        # grid layout ensures buttons line up neatly in two rows
        grid = QGridLayout()
        self.lay.addLayout(grid)

        # create one radio button per available reference option
        self.mean_button    = QRadioButton("mean")
        self.zero_button    = QRadioButton("zero")
        self.initial_button = QRadioButton("initial")
        self.final_button   = QRadioButton("final")

        # add buttons to the grid in logical order
        grid.addWidget(self.mean_button,    0, 0)
        grid.addWidget(self.zero_button,    0, 1)
        grid.addWidget(self.initial_button, 1, 0)
        grid.addWidget(self.final_button,   1, 1)

        # collect controls so we can block signals during programmatic updates
        self._controls = [
            self.mean_button,
            self.zero_button,
            self.initial_button,
            self.final_button
        ]

        # mirror initial snapshot
        self._apply_snapshot(snapshot)

        # connect GUI → emit
        for rb in self._controls:
            rb.toggled.connect(self._emit_math)        

    def update_from_snapshot(self, snap):
        # block signals to prevent handlers firing when syncing controls
        super().update_from_snapshot(snap)
        with self.block_signals(*self._controls):
            self._apply_snapshot(snap)

    def _apply_snapshot(self, snapshot: GuiSnapshot):
        m = RefSpectra(snapshot.math.ref)
        self.mean_button   .setChecked(m is RefSpectra.MEAN)
        self.zero_button   .setChecked(m is RefSpectra.ZERO)
        self.initial_button.setChecked(m is RefSpectra.INITIAL)
        self.final_button  .setChecked(m is RefSpectra.FINAL)

    def _emit_math(self, checked: bool):
        if not checked:                        # ignore “off” transitions
            return

        if self.mean_button.isChecked():
            new_ref = RefSpectra.MEAN
        elif self.zero_button.isChecked():
            new_ref = RefSpectra.ZERO
        elif self.initial_button.isChecked():
            new_ref = RefSpectra.INITIAL
        else:
            new_ref = RefSpectra.FINAL

        new_math: MathSettings = self.snapshot.math.update(ref=new_ref)
        self.state_changed.emit({"math": new_math})
