from PyQt5.QtWidgets import QLabel, QRadioButton, QGridLayout
from PyQt5.QtCore    import Qt

from py2dcos.config.resources import GuiState, RefSpectra
from .base_box import BaseBox

class ReferenceSpectraBox(BaseBox):
    """
    A section for choosing the reference spectra method.

    Emits state_changed with:
      - 'ref_spectra': RefSpectra enum
    """
    def __init__(self, state: GuiState, parent=None):
        super().__init__("Reference Spectra", state, parent)


        # Grid layout for radio buttons
        grid = QGridLayout()
        self.lay.addLayout(grid)

        # Radio buttons
        self.mean_button = QRadioButton("Mean")
        self.zero_button = QRadioButton("Zero")
        self.initial_button = QRadioButton("Initial")
        self.final_button = QRadioButton("Final")

        # Default selection based on state
        current = state.ref_spectra
        self.mean_button.setChecked(current is RefSpectra.MEAN)
        self.zero_button.setChecked(current is RefSpectra.ZERO)
        self.initial_button.setChecked(current is RefSpectra.INITIAL)
        self.final_button.setChecked(current is RefSpectra.FINAL)

        # Place buttons
        grid.addWidget(self.mean_button,   0, 0)
        grid.addWidget(self.zero_button,   0, 1)
        grid.addWidget(self.initial_button,1, 0)
        grid.addWidget(self.final_button,  1, 1)

        # Connect signals
        self.mean_button.toggled.connect(self._on_mean)
        self.zero_button.toggled.connect(self._on_zero)
        self.initial_button.toggled.connect(self._on_initial)
        self.final_button.toggled.connect(self._on_final)

    def _on_mean(self, checked: bool):
        if checked:
            self.state.ref_spectra = RefSpectra.MEAN
            self.state_changed.emit({'ref_spectra': RefSpectra.MEAN})

    def _on_zero(self, checked: bool):
        if checked:
            self.state.ref_spectra = RefSpectra.ZERO
            self.state_changed.emit({'ref_spectra': RefSpectra.ZERO})

    def _on_initial(self, checked: bool):
        if checked:
            self.state.ref_spectra = RefSpectra.INITIAL
            self.state_changed.emit({'ref_spectra': RefSpectra.INITIAL})

    def _on_final(self, checked: bool):
        if checked:
            self.state.ref_spectra = RefSpectra.FINAL
            self.state_changed.emit({'ref_spectra': RefSpectra.FINAL})
