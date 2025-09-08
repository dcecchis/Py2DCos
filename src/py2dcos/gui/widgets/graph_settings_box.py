from PyQt5.QtWidgets import QLabel, QComboBox, QSlider, QGridLayout
from PyQt5.QtCore    import Qt, pyqtSignal
from py2dcos.config.resources import (
    MIN_CONTOURS, MAX_CONTOURS,
    MIN_INTENSITY, MAX_INTENSITY,
    MIN_LINE_INTENSITY, MAX_LINE_INTENSITY,
    LOCATOR_CHOICES, CMAP_LIST, COLOR_LIST
)
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.datatypes import PlotSettings
from .base_box import BaseBox

class GraphSettingsBox(BaseBox):
    """
    a section for contour count, locator, colormap, and intensities.

    emits state_changed with keys:
      - 'num_contours': int
      - 'locator_choice': str
      - 'color_map': str
      - 'contour_line_color': str
      - 'color_map_intensity': float
      - 'contour_lines_intensity': float
    """
    state_changed = pyqtSignal(dict)

    def __init__(self, snapshot: GuiSnapshot, parent=None):
        super().__init__("Graph Settings", snapshot, parent)

        # use grid layout to neatly align labels next to their controls
        self._build_ui()
        self._apply_snapshot(snapshot)

        # connect ui events: update labels live, then emit final values on release or selection
        self.num_slider.valueChanged.connect(lambda v: self.num_label.setText(f"Number of contours: {v}"))
        self.num_slider.sliderReleased.connect(self._emit_plot)
        self.locator_box.activated[str].connect(self._emit_plot)
        self.color_map_box.activated[str].connect(self._emit_plot)
        self.cl_color_box.activated[str].connect(self._emit_plot)
        self.cmap_int_slider.valueChanged.connect(lambda r: self.cmap_int_label.setText(f"Colour intensity: {r}"))
        self.cmap_int_slider.sliderReleased.connect(self._emit_plot)
        self.cl_alpha_slider.valueChanged.connect(lambda r: self.cl_alpha_label.setText(f"Contour-line intensity: {r}"))
        self.cl_alpha_slider.sliderReleased.connect(self._emit_plot)

    def update_from_snapshot(self, snap: GuiSnapshot):
        # block widget signals to prevent triggering handlers during sync
        super().update_from_snapshot(snap)
        with self.block_signals(*self._controls):
            self._apply_snapshot(snap)

    def _apply_snapshot(self, snap: GuiSnapshot):
        p: PlotSettings = snap.plot
        self.num_slider.setValue(p.num_contours)
        self.num_label.setText(f"Number of contours: {p.num_contours}")

        self.locator_box   .setCurrentText(p.locator)
        self.color_map_box .setCurrentText(p.color_map)
        self.cl_color_box  .setCurrentText(p.contour_line_color)

        self.cmap_int_slider.setValue(int(p.color_map_intensity * 100))
        self.cmap_int_label .setText(
            f"Colour intensity: {self.cmap_int_slider.value()}"
        )

        self.cl_alpha_slider.setValue(int(p.contour_line_alpha * 100))
        self.cl_alpha_label.setText(
            f"Contour-line intensity: {self.cl_alpha_slider.value()}"
        )

    def _emit_plot(self, *args):
        #Build new PlotSettings from current widgets and emit
        p_old = self.snapshot.plot
        p_new = p_old.update(
            num_contours          = self.num_slider.value(),
            locator               = self.locator_box.currentText(),
            color_map             = self.color_map_box.currentText(),
            contour_line_color    = self.cl_color_box.currentText(),
            color_map_intensity   = self.cmap_int_slider.value() / 100,
            contour_line_alpha    = self.cl_alpha_slider.value() / 100,
        )
        self.state_changed.emit({"plot": p_new})

    def _build_ui(self):
        grid = QGridLayout()
        grid.setColumnMinimumWidth(0, 160)

        # number of contours
        self.num_label = QLabel()
        self.num_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.num_label, 0, 0)

        self.num_slider = QSlider(Qt.Horizontal)
        self.num_slider.setRange(MIN_CONTOURS, MAX_CONTOURS)
        grid.addWidget(self.num_slider, 0, 1)

        # locator
        grid.addWidget(QLabel("Locator", alignment=Qt.AlignRight), 1, 0)
        self.locator_box = QComboBox()
        self.locator_box.addItems(LOCATOR_CHOICES)
        grid.addWidget(self.locator_box, 1, 1)

        # colour map
        grid.addWidget(QLabel("Colour map", alignment=Qt.AlignRight), 2, 0)
        self.color_map_box = QComboBox()
        self.color_map_box.addItems(CMAP_LIST)
        grid.addWidget(self.color_map_box, 2, 1)

        # contour-line colour
        grid.addWidget(QLabel("Line colour", alignment=Qt.AlignRight), 3, 0)
        self.cl_color_box = QComboBox()
        self.cl_color_box.addItems(COLOR_LIST)
        grid.addWidget(self.cl_color_box, 3, 1)

        # colour-map intensity
        self.cmap_int_label = QLabel()
        self.cmap_int_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.cmap_int_label, 4, 0)

        self.cmap_int_slider = QSlider(Qt.Horizontal)
        self.cmap_int_slider.setRange(MIN_INTENSITY, MAX_INTENSITY)
        grid.addWidget(self.cmap_int_slider, 4, 1)

        # contour-line opacity
        self.cl_alpha_label = QLabel()
        self.cl_alpha_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.cl_alpha_label, 5, 0)

        self.cl_alpha_slider = QSlider(Qt.Horizontal)
        self.cl_alpha_slider.setRange(MIN_LINE_INTENSITY, MAX_LINE_INTENSITY)
        grid.addWidget(self.cl_alpha_slider, 5, 1)

        # store for signal-blocking
        self._controls = [
            self.num_slider, self.locator_box, self.color_map_box,
            self.cl_color_box, self.cmap_int_slider, self.cl_alpha_slider,
        ]
        self.lay.addLayout(grid)