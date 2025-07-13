from PyQt5.QtWidgets import QRadioButton, QGridLayout
from PyQt5.QtCore    import pyqtSignal, Qt
from py2dcos.config.resources import RefSpectra
from .base_box import BaseBox

class ReferenceSpectraBox(BaseBox):
    """
    A section for choosing the reference spectra method.

    Emits state_changed with:
      - 'ref_spectra': RefSpectra enum
    """
    # signal to notify MainWindow of state changes
    state_changed = pyqtSignal(dict)

    def __init__(self, state, parent=None):
        super().__init__("Reference Spectra", state, parent)

        # Grid layout for radio buttons
        grid = QGridLayout()
        self.lay.addLayout(grid)

        # Radio buttons
        self.mean_button    = QRadioButton("Mean")
        self.zero_button    = QRadioButton("Zero")
        self.initial_button = QRadioButton("Initial")
        self.final_button   = QRadioButton("Final")

        self._controls = [self.mean_button, self.zero_button, 
                          self.initial_button, self.final_button]

        # Default selection based on initial state
        current = state.ref_spectra
        self.mean_button.setChecked   (current is RefSpectra.MEAN)
        self.zero_button.setChecked   (current is RefSpectra.ZERO)
        self.initial_button.setChecked(current is RefSpectra.INITIAL)
        self.final_button.setChecked  (current is RefSpectra.FINAL)

        # Place buttons in grid
        grid.addWidget(self.mean_button,    0, 0)
        grid.addWidget(self.zero_button,    0, 1)
        grid.addWidget(self.initial_button, 1, 0)
        grid.addWidget(self.final_button,   1, 1)

        # Connect toggles to handlers
        self.mean_button.toggled.connect   (self._on_mean)
        self.zero_button.toggled.connect   (self._on_zero)
        self.initial_button.toggled.connect(self._on_initial)
        self.final_button.toggled.connect  (self._on_final)

    def update_from_state(self, state):
        with self.block_signals(*self._controls):
            self.mean_button .setChecked(state.ref_spectra is RefSpectra.MEAN)
            self.zero_button .setChecked(state.ref_spectra is RefSpectra.ZERO)
            self.initial_button.setChecked(state.ref_spectra is RefSpectra.INITIAL)
            self.final_button.setChecked(state.ref_spectra is RefSpectra.FINAL)


    def _on_mean(self, checked: bool):
        if checked:
            self.state_changed.emit({'ref_spectra': RefSpectra.MEAN})

    def _on_zero(self, checked: bool):
        if checked:
            self.state_changed.emit({'ref_spectra': RefSpectra.ZERO})

    def _on_initial(self, checked: bool):
        if checked:
            self.state_changed.emit({'ref_spectra': RefSpectra.INITIAL})

    def _on_final(self, checked: bool):
        if checked:
            self.state_changed.emit({'ref_spectra': RefSpectra.FINAL})
