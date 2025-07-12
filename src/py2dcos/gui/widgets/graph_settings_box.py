from PyQt5.QtWidgets import QLabel, QComboBox, QSlider, QGridLayout
from PyQt5.QtCore    import Qt

from py2dcos.config.resources import GuiState, LOCATOR_CHOICES, CMAP_LIST, COLOR_LIST
from .base_box import BaseBox

# Numeric limits (mirror main_window constants)
MIN_CONTOURS = 1
MAX_CONTOURS = 40
MIN_INTENSITY = 0
MAX_INTENSITY = 100
MIN_LINES_INTENSITY = 0
MAX_LINES_INTENSITY = 100

class GraphSettingsBox(BaseBox):
    """
    A section for contour count, locator, colormap, and intensities.

    Emits state_changed with keys:
      - 'num_contours': int
      - 'locator': str
      - 'color_map': str
      - 'contour_line_color': str
      - 'color_map_intensity': float
      - 'contour_line_alpha': float
    """
    def __init__(self, state: GuiState, parent=None):
        super().__init__("Graph Settings", state, parent)

        
        # Grid
        grid = QGridLayout()
        self.lay.addLayout(grid)

        # Number of contours
        self.num_slider = QSlider(Qt.Horizontal)
        self.num_slider.setMinimum(MIN_CONTOURS)
        self.num_slider.setMaximum(MAX_CONTOURS)
        self.num_slider.setValue(getattr(state, 'num_contours', 6))
        grid.addWidget(self.num_slider, 0, 1)
        self.num_label = QLabel(f"Number of Contours: {self.num_slider.value()}")
        self.num_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.num_label, 0, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)

        # Locator
        grid.addWidget(QLabel("Locator"), 1, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.locator_box = QComboBox()
        self.locator_box.addItems(LOCATOR_CHOICES)
        self.locator_box.setCurrentText(getattr(state, 'locator', LOCATOR_CHOICES[0]))
        grid.addWidget(self.locator_box, 1, 1)

        # Color Map
        grid.addWidget(QLabel("Color Map"), 2, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.color_map_box = QComboBox()
        self.color_map_box.addItems(CMAP_LIST)
        self.color_map_box.setCurrentText(getattr(state, 'color_map', CMAP_LIST[0]))
        grid.addWidget(self.color_map_box, 2, 1)

        # Contour Lines Color
        grid.addWidget(QLabel("Contour Lines Color"), 3, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.cl_color_box = QComboBox()
        self.cl_color_box.addItems(COLOR_LIST)
        self.cl_color_box.setCurrentText(getattr(state, 'contour_line_color', COLOR_LIST[0]))
        grid.addWidget(self.cl_color_box, 3, 1)

        # Color intensity
        self.cmap_int_slider = QSlider(Qt.Horizontal)
        self.cmap_int_slider.setMinimum(MIN_INTENSITY)
        self.cmap_int_slider.setMaximum(MAX_INTENSITY)
        self.cmap_int_slider.setValue(int(getattr(state, 'color_map_intensity', 1.0)*100))
        grid.addWidget(self.cmap_int_slider, 4, 1)
        self.cmap_int_label = QLabel(f"Color Intensity: {self.cmap_int_slider.value()}")
        self.cmap_int_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.cmap_int_label, 4, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)

        # Contour lines intensity
        self.cl_alpha_slider = QSlider(Qt.Horizontal)
        self.cl_alpha_slider.setMinimum(MIN_LINES_INTENSITY)
        self.cl_alpha_slider.setMaximum(MAX_LINES_INTENSITY)
        self.cl_alpha_slider.setValue(int(getattr(state, 'contour_line_alpha', 0.6)*100))
        grid.addWidget(self.cl_alpha_slider, 5, 1)
        self.cl_alpha_label = QLabel(f"Contour Lines Intensity: {self.cl_alpha_slider.value()}")
        self.cl_alpha_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.cl_alpha_label, 5, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)

        # Connect signals
        self.num_slider.valueChanged.connect(self._on_num_changed)
        self.num_slider.sliderReleased.connect(self._emit_num)
        self.locator_box.activated[str].connect(self._on_locator)
        self.color_map_box.activated[str].connect(self._on_cmap)
        self.cl_color_box.activated[str].connect(self._on_cl_color)
        self.cmap_int_slider.valueChanged.connect(self._on_cmap_int_changed)
        self.cmap_int_slider.sliderReleased.connect(self._emit_cmap_int)
        self.cl_alpha_slider.valueChanged.connect(self._on_cl_alpha_changed)
        self.cl_alpha_slider.sliderReleased.connect(self._emit_cl_alpha)

    def _on_num_changed(self, val: int):
        self.num_label.setText(f"Number of Contours: {val}")

    def _emit_num(self):
        val = self.num_slider.value()
        self.state.num_contours = val
        self.state_changed.emit({'num_of_contours': val})

    def _on_locator(self, text: str):
        self.state.locator = text
        self.state_changed.emit({'locator_choice': text})

    def _on_cmap(self, text: str):
        self.state.color_map = text
        self.state_changed.emit({'color_map': text})

    def _on_cl_color(self, text: str):
        self.state.contour_line_color = text
        self.state_changed.emit({'contour_line_color': text})

    def _on_cmap_int_changed(self, raw: int):
        self.cmap_int_label.setText(f"Color Intensity: {raw}")

    def _emit_cmap_int(self):
        val = self.cmap_int_slider.value() / 100
        self.state.color_map_intensity = val
        self.state_changed.emit({'color_map_intensity': val})

    def _on_cl_alpha_changed(self, raw: int):
        self.cl_alpha_label.setText(f"Contour Lines Intensity: {raw}")

    def _emit_cl_alpha(self):
        val = self.cl_alpha_slider.value() / 100
        self.state.contour_line_intensity = val
        self.state_changed.emit({'contour_lines_intensity': val})
