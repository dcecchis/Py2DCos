from PyQt5.QtWidgets import QLabel, QComboBox, QSlider, QCheckBox, QGridLayout
from PyQt5.QtCore    import Qt, pyqtSignal
import logging

from .base_box import BaseBox

# Numeric limits for Gaussian smoothing slider
MIN_GAUSSIAN = 0
MAX_GAUSSIAN = 5


class DataTreatmentBox(BaseBox):
    """
    Section for PCA reconstruction components, Gaussian smoothing, and node attenuation.

    Emits state_changed with keys:
      - 'reconstruction_components': int
      - 'sigma_gaussian': float
      - 'node_attenuation': bool
    """
    state_changed = pyqtSignal(dict)

    def __init__(self, state, parent=None):
        super().__init__("Data Treatment", state, parent)

        # Layout
        grid = QGridLayout()
        grid.setColumnMinimumWidth(0, 140)
        self.lay.addLayout(grid)

        # PCA reconstruction components
        pca_label = QLabel("Components for PCA reconstruction")
        pca_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(pca_label, 0, 0)
        self.pca_combo = QComboBox()
        for i in range(9):
            self.pca_combo.addItem(str(i))
        self.pca_combo.setCurrentText(str(state.reconstruction_components))
        grid.addWidget(self.pca_combo, 0, 1)

        # Gaussian smoothing slider
        self.gaussian_slider = QSlider(Qt.Horizontal)
        self.gaussian_slider.setMinimum(MIN_GAUSSIAN)
        self.gaussian_slider.setMaximum(MAX_GAUSSIAN)
        self.gaussian_slider.setValue(state.sigma_gaussian)
        grid.addWidget(self.gaussian_slider, 1, 1)
        self.gaussian_label = QLabel(f"Gaussian Smoothing: {self.gaussian_slider.value()}")
        self.gaussian_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.gaussian_label, 1, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)

        # Node attenuation filter
        node_label = QLabel("Apply Node Attenuation Filter")
        node_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(node_label, 2, 0)
        self.node_checkbox = QCheckBox()
        self.node_checkbox.setChecked(state.node_attenuation)
        grid.addWidget(self.node_checkbox, 2, 1)

        self._controls = [self.pca_combo, self.gaussian_slider, self.node_checkbox]

        # Connect UI events
        self.pca_combo.activated[str].connect(self._on_pca_changed)
        self.gaussian_slider.valueChanged.connect(self._on_gaussian_value_changed)
        self.gaussian_slider.sliderReleased.connect(self._emit_gaussian)
        self.node_checkbox.clicked.connect(self._emit_node)

    def update_from_state(self, state):
        with self.block_signals(*self._controls):
            # PCA components
            self.pca_combo.setCurrentText(str(state.reconstruction_components))
            # Gaussian
            self.gaussian_slider.setValue(state.sigma_gaussian)
            self.gaussian_label .setText(f"Gaussian Smoothing: {state.sigma_gaussian}")
            # Node attenuation
            self.node_checkbox .setChecked(state.node_attenuation)

    def _on_pca_changed(self, text: str):
        try:
            val = int(text)
            self.state_changed.emit({'reconstruction_components': val})
        except ValueError:
            logging.warning("Invalid PCA components selection: %s", text)

    def _on_gaussian_value_changed(self, raw: int):
        self.gaussian_label.setText(f"Gaussian Smoothing: {raw}")

    def _emit_gaussian(self):
        val = self.gaussian_slider.value()
        self.state_changed.emit({'sigma_gaussian': val})

    def _emit_node(self, checked: bool):
        self.state_changed.emit({'node_attenuation': checked})
