from PyQt5.QtWidgets import QLabel, QComboBox, QSlider, QCheckBox, QGridLayout
from PyQt5.QtCore    import Qt
import logging

from py2dcos.config.resources import GuiState
from .base_box import BaseBox

# Mirror the constants from the main window
MIN_GAUSSIAN = 0
MAX_GAUSSIAN = 5

class DataTreatmentBox(BaseBox):
    """
    A section for PCA reconstruction components, Gaussian smoothing, and node attenuation.

    Emits state_changed with keys:
      - 'reconstruction_components': int
      - 'sigma_gaussian': float
      - 'node_attenuation': bool
    """
    def __init__(self, state: GuiState, parent=None):
        super().__init__("Data Treatment", state, parent)

        # Grid layout
        grid = QGridLayout()
        grid.setColumnMinimumWidth(0, 140)
        self.lay.addLayout(grid)

        # PCA reconstruction components
        pca_label = QLabel("Components for PCA reconstruction")
        pca_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(pca_label, 0, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.pca_combo = QComboBox()
        for i in range(0, 9):
            self.pca_combo.addItem(str(i))
        # Default from state
        self.pca_combo.setCurrentText(str(getattr(state, 'reconstruction_components', 0)))
        grid.addWidget(self.pca_combo, 0, 1)

        # Gaussian smoothing slider
        self.gaussian_slider = QSlider(Qt.Horizontal)
        self.gaussian_slider.setMinimum(MIN_GAUSSIAN)
        self.gaussian_slider.setMaximum(MAX_GAUSSIAN)
        self.gaussian_slider.setValue(int(getattr(state, 'sigma_gaussian', 0)))
        grid.addWidget(self.gaussian_slider, 1, 1)
        self.gaussian_label = QLabel(f"Gaussian Smoothing: {self.gaussian_slider.value()}")
        self.gaussian_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.gaussian_label, 1, 0, alignment=Qt.AlignRight | Qt.AlignVCenter) 

        # Node attenuation filter checkbox
        node_label = QLabel("Apply Node Attenuation Filter")
        node_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(node_label, 2, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.node_checkbox = QCheckBox()
        self.node_checkbox.setChecked(bool(getattr(state, 'node_attenuation', False)))
        grid.addWidget(self.node_checkbox, 2, 1)

        # Signal connections
        self.pca_combo.activated[str].connect(self._on_pca_changed)
        self.gaussian_slider.valueChanged.connect(self._on_gaussian_value_changed)
        self.gaussian_slider.sliderReleased.connect(self._on_gaussian_released)
        self.node_checkbox.clicked.connect(self._on_node_toggled)

    def _on_pca_changed(self, text: str):
        try:
            val = int(text)
            self.state.reconstruction_components = val
            self.state_changed.emit({'reconstruction_components': val})
        except ValueError:
            logging.warning("Invalid PCA components selection: %s", text)

    def _on_gaussian_value_changed(self, raw: int):
        # update label live
        self.gaussian_label.setText(f"Gaussian Smoothing: {raw}")

    def _on_gaussian_released(self):
        val = self.gaussian_slider.value()
        self.state.sigma_gaussian = val
        self.state_changed.emit({'sigma_gaussian': val})

    def _on_node_toggled(self, checked: bool):
        self.state.node_attenuation = checked
        self.state_changed.emit({'node_attenuation': checked})
