from PyQt5.QtWidgets import QRadioButton, QGridLayout
from PyQt5.QtCore    import pyqtSignal, Qt
from py2dcos.config.resources import RefSpectra
from .base_box import BaseBox

class ReferenceSpectraBox(BaseBox):
    """
    a section for choosing the reference spectra method.

    emits state_changed with:
      - 'ref_spectra': refspectra enum
    """
    # notify main window when user picks a different reference method
    state_changed = pyqtSignal(dict)

    def __init__(self, state, parent=None):
        super().__init__("Reference Spectra", state, parent)

        # grid layout ensures buttons line up neatly in two rows
        grid = QGridLayout()
        self.lay.addLayout(grid)

        # create one radio button per available reference option
        self.mean_button    = QRadioButton("mean")
        self.zero_button    = QRadioButton("zero")
        self.initial_button = QRadioButton("initial")
        self.final_button   = QRadioButton("final")

        # collect controls so we can block signals during programmatic updates
        self._controls = [
            self.mean_button,
            self.zero_button,
            self.initial_button,
            self.final_button
        ]

        # set initial selection to match current gui state
        current = state.ref_spectra
        self.mean_button   .setChecked(current is RefSpectra.MEAN)
        self.zero_button   .setChecked(current is RefSpectra.ZERO)
        self.initial_button.setChecked(current is RefSpectra.INITIAL)
        self.final_button  .setChecked(current is RefSpectra.FINAL)

        # add buttons to the grid in logical order
        grid.addWidget(self.mean_button,    0, 0)
        grid.addWidget(self.zero_button,    0, 1)
        grid.addWidget(self.initial_button, 1, 0)
        grid.addWidget(self.final_button,   1, 1)

        # connect each toggle to its handler to emit the correct enum value
        self.mean_button.toggled.connect   (self._on_mean)
        self.zero_button.toggled.connect   (self._on_zero)
        self.initial_button.toggled.connect(self._on_initial)
        self.final_button.toggled.connect  (self._on_final)

    def update_from_state(self, state):
        # block signals to prevent handlers firing when syncing controls
        with self.block_signals(*self._controls):
            self.mean_button   .setChecked(state.ref_spectra is RefSpectra.MEAN)
            self.zero_button   .setChecked(state.ref_spectra is RefSpectra.ZERO)
            self.initial_button.setChecked(state.ref_spectra is RefSpectra.INITIAL)
            self.final_button  .setChecked(state.ref_spectra is RefSpectra.FINAL)

    def _on_mean(self, checked: bool):
        # only emit when the mean option is activated
        if checked:
            self.state_changed.emit({'ref_spectra': RefSpectra.MEAN})

    def _on_zero(self, checked: bool):
        # only emit when the zero option is activated
        if checked:
            self.state_changed.emit({'ref_spectra': RefSpectra.ZERO})

    def _on_initial(self, checked: bool):
        # only emit when the initial option iss activated
        if checked:
            self.state_changed.emit({'ref_spectra': RefSpectra.INITIAL})

    def _on_final(self, checked: bool):
        # oew final option is activated
        if checked:
            self.state_changed.emit({'ref_spectra': RefSpectra.FINAL})
