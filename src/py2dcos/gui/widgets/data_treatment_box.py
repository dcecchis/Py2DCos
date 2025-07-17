from PyQt5.QtWidgets import QLabel, QComboBox, QSlider, QCheckBox, QGridLayout
from PyQt5.QtCore    import Qt, pyqtSignal
import logging

from .base_box import BaseBox

# define slider range for gaussian smoothing to prevent invalid values
MIN_GAUSSIAN = 0
MAX_GAUSSIAN = 5

class DataTreatmentBox(BaseBox):
    """
    section for pca reconstruction components, gaussian smoothing, and node attenuation.

    emits state_changed with keys:
      - 'reconstruction_components': int
      - 'sigma_gaussian': float
      - 'node_attenuation': bool
    """
    state_changed = pyqtSignal(dict)

    def __init__(self, state, parent=None):
        super().__init__("Data Treatment", state, parent)

        # use grid layout to align labels and controls in rows
        grid = QGridLayout()
        grid.setColumnMinimumWidth(0, 140)  # ensure label column is wide enough
        self.lay.addLayout(grid)

        # pca reconstruction components dropdown
        pca_label = QLabel("Components for PCA reconstruction")
        pca_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(pca_label, 0, 0)
        self.pca_combo = QComboBox()
        # offer choices 0–8 for number of components
        for i in range(9):
            self.pca_combo.addItem(str(i))
        # initialize to current state value
        self.pca_combo.setCurrentText(str(state.reconstruction_components))
        grid.addWidget(self.pca_combo, 0, 1)

        # gaussian smoothing slider setup
        self.gaussian_slider = QSlider(Qt.Horizontal)
        self.gaussian_slider.setMinimum(MIN_GAUSSIAN)  # avoid negative sigma
        self.gaussian_slider.setMaximum(MAX_GAUSSIAN)  # cap smoothing intensity
        self.gaussian_slider.setValue(state.sigma_gaussian)
        grid.addWidget(self.gaussian_slider, 1, 1)
        # label to show current smoothing value
        self.gaussian_label = QLabel(f"Gaussian smoothing: {self.gaussian_slider.value()}")
        self.gaussian_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(
            self.gaussian_label,
            1, 0,
            alignment=Qt.AlignRight | Qt.AlignVCenter
        )

        # node attenuation filter toggle
        node_label = QLabel("Apply Node attenuation filter")
        node_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(node_label, 2, 0)
        self.node_checkbox = QCheckBox()
        # reflect initial state of node attenuation
        self.node_checkbox.setChecked(state.node_attenuation)
        grid.addWidget(self.node_checkbox, 2, 1)

        # collect controls for signal-blocking during updates
        self._controls = [self.pca_combo, self.gaussian_slider, self.node_checkbox]

        # connect ui events to handlers that emit state changes
        self.pca_combo.activated[str].connect(self._on_pca_changed)
        self.gaussian_slider.valueChanged.connect(self._on_gaussian_value_changed)
        self.gaussian_slider.sliderReleased.connect(self._emit_gaussian)
        self.node_checkbox.clicked.connect(self._emit_node)

    def update_from_state(self, state):
        # block signals to avoid feedback loops when syncing controls from state
        with self.block_signals(*self._controls):
            # update dropdown to match new reconstruction setting
            self.pca_combo.setCurrentText(str(state.reconstruction_components))
            # update slider and label to match new gaussian sigma
            self.gaussian_slider.setValue(state.sigma_gaussian)
            self.gaussian_label.setText(f"Gaussian smoothing: {state.sigma_gaussian}")
            # update checkbox to match node attenuation flag
            self.node_checkbox.setChecked(state.node_attenuation)

    def _on_pca_changed(self, text: str):
        # convert selected text to int; warn if conversion fails
        try:
            val = int(text)
            self.state_changed.emit({'reconstruction_components': val})
        except ValueError:
            logging.warning("Invalid PCA components selection: %s", text)

    def _on_gaussian_value_changed(self, raw: int):
        # live-update label while user moves slider
        self.gaussian_label.setText(f"Gaussian smoothing: {raw}")

    def _emit_gaussian(self):
        # emit final smoothing value after slider release
        val = self.gaussian_slider.value()
        self.state_changed.emit({'sigma_gaussian': val})

    def _emit_node(self, checked: bool):
        # emit updated node attenuation toggle state
        self.state_changed.emit({'node_attenuation': checked})
