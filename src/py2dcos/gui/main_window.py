import logging
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QScrollArea,
    QPushButton, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from py2dcos.plotting.backends.plotly_backend import PlotlyBackend
from py2dcos.config.resources import CorrType, ShownGraph
from py2dcos.gui.state import GuiState
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
        self.backend3d = PlotlyBackend(webview=self.webview)
        self._on_state_change({'show_3d': self.state.show_3d})

    def _init_variables(self):
        self.plot_ready = False
        self.state = GuiState()

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

        self.webview = QWebEngineView()
        self.webview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.webview.hide()
        right_layout.addWidget(self.webview)

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

        if "corr_type" in delta:
            input_box = self.boxes[1]
            is_hetero = (self.state.corr_type is CorrType.HETERO)
            input_box.file2_button.setVisible(is_hetero)

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
        
        # --- 3-D / 2-D toggle & update ---
        if {'show_3d', 'shown_graph'} & delta.keys():
            if self.state.show_3d:
                which = 'sync'
                if self.state.shown_graph is ShownGraph.ASYNC:
                    which = 'async'
                # Both defaults to sync
                self.backend3d.plot3d(
                    self.correlation_model,
                    self.state.color_map,
                    which=which
                )
                self.canvas.hide()
                self.toolbar.hide()
                self.webview.show()

                # Force immediate WebGL resize so the figure renders
                self.webview.page().runJavaScript(
                    "window.dispatchEvent(new Event('resize'));"
                )

                self.tridimensional_button.setText("Show 2D Plot")
            else:
                self.webview.hide()
                self.toolbar.show()
                self.canvas.show()
                self.canvas.draw()
                self.tridimensional_button.setText("Show 3D Plot")

    def setup_signals(self):
        self.plot_button.clicked.connect(self.plot_button_function)
        self.tridimensional_button.setCheckable(True)
        self.tridimensional_button.clicked.connect(self._on_3d_button)

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

    def _on_3d_button(self):
        # ensure 2D plot exists before trying to go 3D
        if not getattr(self, 'correlation_model', None):
            QMessageBox.information(self, 'Information',
                'Please generate the 2D correlation plot first.')
            # keep the button state consistent
            self.tridimensional_button.setChecked(self.state.show_3d)
            return

        # flip the flag
        new_flag = not self.state.show_3d
        self._set_state(show_3d=new_flag)
        # immediately run your show_3d logic
        self._on_state_change({'show_3d': new_flag})

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
