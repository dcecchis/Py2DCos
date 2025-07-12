import logging
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QScrollArea,
    QPushButton, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from py2dcos.config.resources import GuiState, CorrType
from py2dcos.controller.app_controller import AppController
from py2dcos.plotting.correlation_plot import CorrelationPlotter
from py2dcos.gui.widgets import (
    CorrelationTypeBox,
    InputFilesBox,
    DataTreatmentBox,
    ReferenceSpectraBox,
    GraphSettingsBox,
    DiagonalsAxesBox,
    ShownGraphBox,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._init_variables()
        self.setWindowTitle("Py2DCoS")
        self.build_ui()
        self.setup_signals()
        self.controller = AppController()

    def _init_variables(self):
        self.plot_ready = False
        self.state = GuiState()

    def _set_state(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.state, key, value)
            logging.info("Updated %s: %s", key, value)

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Left scroll panel
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)

        self.boxes = [
            CorrelationTypeBox(self.state),
            InputFilesBox(self.state),
            DataTreatmentBox(self.state),
            ReferenceSpectraBox(self.state),
            GraphSettingsBox(self.state),
            DiagonalsAxesBox(self.state),
            ShownGraphBox(self.state),
        ]
        for box in self.boxes:
            left_layout.addWidget(box)

        # Plot button
        self.plot_button = QPushButton("Plot")
        self.plot_button.setFont(self.get_font_title())
        self.plot_button.setFixedSize(250, 50)
        left_layout.addWidget(self.plot_button, alignment=Qt.AlignHCenter)
        left_layout.addStretch()

        scroll.setWidget(left_container)
        main_layout.addWidget(scroll, 2)

        # Connect all box signals
        for box in self.boxes:
            box.state_changed.connect(self._on_state_change)

        # Right plot area
        self._create_plot_area(main_layout)

    def _create_plot_area(self, parent_layout):
        right_layout = QVBoxLayout()
        self.figure = plt.figure()
        self.figure.set_facecolor("#f0f0f0")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(self.canvas)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.addStretch(1)
        self.toolbar = NavigationToolbar(self.canvas, parent=self)
        toolbar_layout.addWidget(self.toolbar)
        self.tridimensional_button = QPushButton("Show 3D Plot")
        toolbar_layout.addWidget(self.tridimensional_button)
        toolbar_layout.addStretch(1)
        right_layout.addLayout(toolbar_layout)

        parent_layout.addLayout(right_layout, 5)

    def _on_state_change(self, delta: dict):
        # Merge all changes straight into GuiState
        self._set_state(**delta)

        # If plot exists and some fields changed, recalc then redraw
        recalc_fields = {
            'corr_type', 'ref_spectra', 'reconstruction_components',
            'node_attenuation', 'sigma_gaussian'
        }
        if self.plot_ready and recalc_fields & delta.keys():
            self.recalculate_correlation()

        if self.plot_ready:
            self.plotter.plot(
                shownGraph=self.state.shown_graph.name.lower(),
                **self.get_plot_args()
            )
            self.canvas.draw()

    def setup_signals(self):
        self.plot_button.clicked.connect(self.plot_button_function)
        self.tridimensional_button.clicked.connect(self.plot_tridimensional)

    def plot_button_function(self):
        try:
            file1 = self.state.filename1
            file2 = self.state.filename2

            if not file1:
                QMessageBox.warning(self, 'Missing File', 'Please choose at least one input file.')
                return
            if self.state.corr_type is CorrType.HOMO:
                file2 = file1

            elif not file2:
                QMessageBox.warning(
                    self, 'Missing Second File',
                    'Choose the second file for heterocorrelation or switch to homocorrelation.'
                )
                return

            if self.state.format1 == "xlsx" and self.state.excel_params1:
                file1 = (*file1, *self.state.excel_params1)
                if self.state.corr_type is CorrType.HOMO:
                    file2 = file1

            if file2 and self.state.format2 == "xlsx" and self.state.excel_params2:
                file2 = (*file2, *self.state.excel_params2)

            self.correlation_model = self.controller.build_model(
                file1, file2, self.state
            )
            if not self.correlation_model:
                return

            self.plotter = CorrelationPlotter(
                model=self.correlation_model,
                figure=self.figure,
                canvas=self.canvas
            )
            self.plotter.plot(
                shownGraph=self.state.shown_graph.name.lower(),
                **self.get_plot_args()
            )
            self.plot_ready = True
            logging.info("Plot generated successfully.")

        except ValueError as ve:
            logging.warning("Validation Error: %s", ve)
            QMessageBox.warning(self, 'Validation Error', str(ve))
        except Exception as e:
            logging.exception("Unexpected error in plot_button_function")
            QMessageBox.critical(self, 'Unexpected Error', str(e))

    def plot_tridimensional(self):
        if not getattr(self, 'correlation_model', None):
            QMessageBox.information(self, 'Information', 'Please generate the 2D correlation plot first.')
            return
        try:
            self.plotter.plot3d(color_map=self.state.color_map)
            logging.info("3D plot generated successfully.")
        except Exception as e:
            logging.exception("Error generating 3D plot.")
            QMessageBox.critical(self, '3D Plot Error', str(e))

    def recalculate_correlation(self):
        try:
            method = self.state.calc_method.value
            logging.info("Recalculating correlation using method: %s", method)
            self.correlation_model.syn(method=method)
            self.correlation_model.asyn(method=method)
            logging.info("Correlation recomputation completed.")
        except Exception as e:
            logging.exception("Error during recalculation")
            QMessageBox.critical(self, 'Calculation Error', str(e))

    def get_plot_args(self) -> dict:
        return {
            'color_map': self.state.color_map,
            'num_contours': self.state.num_of_contours,
            'locator': self.state.locator_choice,
            'sync_diag': self.state.sync_diag.value,
            'async_diag': self.state.async_diag.value,
            'x_axis': self.state.x_axis.value,
            'color_map_intensity': self.state.color_map_intensity,
            'contour_line_color': self.state.contour_line_color,
            'contour_line_alpha': self.state.contour_lines_intensity,
            'peaks': self.state.peaks_signs,
        }

    def get_font_title(self):
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        return font

    def get_font_text(self):
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        return font
