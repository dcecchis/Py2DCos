from PyQt5.QtWidgets import QLabel, QComboBox, QSlider, QGridLayout
from PyQt5.QtCore    import Qt, pyqtSignal
from py2dcos.config.resources import (
    MIN_CONTOURS, MAX_CONTOURS,
    MIN_INTENSITY, MAX_INTENSITY,
    MIN_LINE_INTENSITY, MAX_LINE_INTENSITY,
    LOCATOR_CHOICES, CMAP_LIST, COLOR_LIST
)
from py2dcos.gui.state import GuiState
from .base_box import BaseBox


class GraphSettingsBox(BaseBox):
    """
    A section for contour count, locator, colormap, and intensities.

    Emits state_changed with keys:
      - 'num_contours': int
      - 'locator_choice': str
      - 'color_map': str
      - 'contour_line_color': str
      - 'color_map_intensity': float
      - 'contour_lines_intensity': float
    """
    state_changed = pyqtSignal(dict)

    def __init__(self, state, parent=None):
        super().__init__("Graph Settings", state, parent)

        # Grid layout
        grid = QGridLayout()
        self.lay.addLayout(grid)

        # Number of contours
        self.num_slider = QSlider(Qt.Horizontal)
        self.num_slider.setMinimum(MIN_CONTOURS)
        self.num_slider.setMaximum(MAX_CONTOURS)
        self.num_slider.setValue(state.num_contours)
        grid.addWidget(self.num_slider, 0, 1)
        self.num_label = QLabel(f"Number of Contours: {self.num_slider.value()}")
        self.num_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.num_label, 0, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)

        # Locator
        grid.addWidget(QLabel("Locator"), 1, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.locator_box = QComboBox()
        self.locator_box.addItems(LOCATOR_CHOICES)
        self.locator_box.setCurrentText(state.locator_choice)
        grid.addWidget(self.locator_box, 1, 1)

        # Color map
        grid.addWidget(QLabel("Color Map"), 2, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.color_map_box = QComboBox()
        self.color_map_box.addItems(CMAP_LIST)
        self.color_map_box.setCurrentText(state.color_map)
        grid.addWidget(self.color_map_box, 2, 1)

        # Contour lines color
        grid.addWidget(QLabel("Contour Lines Color"), 3, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.cl_color_box = QComboBox()
        self.cl_color_box.addItems(COLOR_LIST)
        self.cl_color_box.setCurrentText(state.contour_line_color)
        grid.addWidget(self.cl_color_box, 3, 1)

        # Color intensity slider
        self.cmap_int_slider = QSlider(Qt.Horizontal)
        self.cmap_int_slider.setMinimum(MIN_INTENSITY)
        self.cmap_int_slider.setMaximum(MAX_INTENSITY)
        self.cmap_int_slider.setValue(int(state.color_map_intensity * 100))
        grid.addWidget(self.cmap_int_slider, 4, 1)
        self.cmap_int_label = QLabel(f"Color Intensity: {self.cmap_int_slider.value()}")
        self.cmap_int_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.cmap_int_label, 4, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)

        # Contour lines intensity slider
        self.cl_alpha_slider = QSlider(Qt.Horizontal)
        self.cl_alpha_slider.setMinimum(MIN_LINE_INTENSITY)
        self.cl_alpha_slider.setMaximum(MAX_LINE_INTENSITY)
        self.cl_alpha_slider.setValue(int(state.contour_lines_intensity * 100))
        grid.addWidget(self.cl_alpha_slider, 5, 1)
        self.cl_alpha_label = QLabel(f"Contour Lines Intensity: {self.cl_alpha_slider.value()}")
        self.cl_alpha_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.cl_alpha_label, 5, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
    
        self._controls = [self.num_slider, self.locator_box, self.color_map_box, self.cl_color_box,
                          self.cmap_int_slider, self.cl_alpha_slider]

        # Connect UI events to handlers
        self.num_slider.valueChanged.connect(self._on_num_changed)
        self.num_slider.sliderReleased.connect(self._emit_num)
        self.locator_box.activated[str].connect(self._emit_locator)
        self.color_map_box.activated[str].connect(self._emit_cmap)
        self.cl_color_box.activated[str].connect(self._emit_cl_color)
        self.cmap_int_slider.valueChanged.connect(self._on_cmap_int_changed)
        self.cmap_int_slider.sliderReleased.connect(self._emit_cmap_int)
        self.cl_alpha_slider.valueChanged.connect(self._on_cl_alpha_changed)
        self.cl_alpha_slider.sliderReleased.connect(self._emit_cl_alpha)
        
    def update_from_state(self, state):
        with self.block_signals(*self._controls):
            self.num_slider         .setValue(state.num_contours)
            self.num_label          .setText(f"Number of Contours: {state.num_contours}")
            self.locator_box        .setCurrentText(state.locator_choice)
            self.color_map_box      .setCurrentText(state.color_map)
            self.cl_color_box       .setCurrentText(state.contour_line_color)
            self.cmap_int_slider    .setValue(int(state.color_map_intensity*100))
            self.cmap_int_label     .setText(f"Color Intensity: {self.cmap_int_slider.value()}")
            self.cl_alpha_slider    .setValue(int(state.contour_lines_intensity*100))
            self.cl_alpha_label     .setText(f"Contour Lines Intensity: {self.cl_alpha_slider.value()}")

    def _on_num_changed(self, val: int):
        self.num_label.setText(f"Number of Contours: {val}")

    def _emit_num(self):
        val = self.num_slider.value()
        self.state_changed.emit({'num_contours': val})

    def _emit_locator(self, text: str):
        self.state_changed.emit({'locator_choice': text})

    def _emit_cmap(self, text: str):
        self.state_changed.emit({'color_map': text})

    def _emit_cl_color(self, text: str):
        self.state_changed.emit({'contour_line_color': text})

    def _on_cmap_int_changed(self, raw: int):
        self.cmap_int_label.setText(f"Color Intensity: {raw}")

    def _emit_cmap_int(self):
        val = self.cmap_int_slider.value() / 100
        self.state_changed.emit({'color_map_intensity': val})

    def _on_cl_alpha_changed(self, raw: int):
        self.cl_alpha_label.setText(f"Contour Lines Intensity: {raw}")

    def _emit_cl_alpha(self):
        val = self.cl_alpha_slider.value() / 100
        self.state_changed.emit({'contour_lines_intensity': val})
