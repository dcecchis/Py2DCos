from PyQt5.QtWidgets import QLabel, QComboBox, QSlider, QCheckBox, QGridLayout
from PyQt5.QtCore    import Qt, pyqtSignal
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.types import MathSettings
from py2dcos.config.resources import MIN_GAUSSIAN, MAX_GAUSSIAN
import logging

from .base_box import BaseBox


class DataTreatmentBox(BaseBox):
    """
    section for pca reconstruction components, gaussian smoothing, and node attenuation.

    emits state_changed with keys:
      - 'reconstruction_components': int
      - 'sigma_gaussian': float
      - 'node_attenuation': bool
    """
    state_changed = pyqtSignal(dict)

    def __init__(self, snapshot: GuiSnapshot, parent=None):
        super().__init__("Data Treatment", snapshot, parent)

        self._build_ui()
        self._apply_snapshot(snapshot)

        # connect ui events to handlers that emit state changes
        self.pca_combo.activated[str].connect(self._emit_math)
        self.gaussian_slider.sliderReleased.connect(self._emit_math)
        self.gaussian_slider.valueChanged.connect(self._update_gauss_label)
        self.node_checkbox.clicked.connect(self._emit_math)

    @staticmethod
    def _make_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return lbl
    
    def _apply_snapshot(self, snapshot: GuiSnapshot):
        m: MathSettings = snapshot.math
        self.pca_combo.setCurrentText(str(m.reconstruction_comps))
        self.gaussian_slider.setValue(int(m.sigma_gaussian))
        self.gaussian_label.setText(f"Gaussian smoothing: {m.sigma_gaussian}")
        self.node_checkbox.setChecked(m.node_attenuation)


    def update_from_snapshot(self, snapshot: GuiSnapshot):
        # block signals to avoid feedback loops when syncing controls from state
        super().update_from_snapshot(snapshot)
        with self.block_signals(*self._controls):
            self._apply_snapshot(snapshot)

    def _emit_math(self) -> None:
        """Build MathSettings reflecting current widgets."""

        comps = int(self.pca_combo.currentText())

        new_math = self.snapshot.math.update(
            reconstruction_comps=comps,
            sigma_gaussian=float(self.gaussian_slider.value()),
            node_attenuation=self.node_checkbox.isChecked(),
        )
        self.state_changed.emit({"math": new_math})

    def _update_gauss_label(self, raw: int) -> None:
        self.gaussian_label.setText(f"Gaussian smoothing: {raw}")
        
    def _build_ui(self) -> None:
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
        grid.addWidget(self.pca_combo, 0, 1)

        # gaussian smoothing slider setup
        self.gaussian_slider = QSlider(Qt.Horizontal)
        self.gaussian_slider.setMinimum(MIN_GAUSSIAN)  # avoid negative sigma
        self.gaussian_slider.setMaximum(MAX_GAUSSIAN)  # cap smoothing intensity
        grid.addWidget(self.gaussian_slider, 1, 1)
        # label to show current smoothing value
        self.gaussian_label = QLabel(f"Gaussian smoothing: 0")
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
        grid.addWidget(self.node_checkbox, 2, 1)

        # collect controls for signal-blocking during updates
        self._controls = [self.pca_combo, self.gaussian_slider, self.node_checkbox]
