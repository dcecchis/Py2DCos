import logging
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QScrollArea,
    QPushButton, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from py2dcos.config.resources import CorrType, ShownGraph
from py2dcos.gui.state import GuiState
from py2dcos.controller.app_controller import AppController
from py2dcos.plotting.backends.plotly_backend import PlotlyBackend
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

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class MainWindow(QMainWindow):
    """
    The main application window. Holds the single GuiState instance,
    routes widget state_changed signals into that state, and drives plotting.
    """
    def __init__(self):
        super().__init__()
        self.state = GuiState()
        self.plot_ready = False

        self.setWindowTitle("Py2DCoS")
        self._build_ui()
        self._setup_signals()

        # Core controller and 3D backend
        self.controller = AppController()
        self.backend3d = PlotlyBackend(webview=self.webview)

        # Initialize UI from state
        self._apply_state({})  # no-op, but pushes initial state into widgets

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Left panel: all our parameter boxes
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
        left_layout.addWidget(self.plot_button, alignment=Qt.AlignHCenter)
        left_layout.addStretch()

        scroll.setWidget(left_container)
        main_layout.addWidget(scroll, 2)

        # Right panel: plotting canvas and toolbar
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
        self.tridimensional_button.setCheckable(True)
        toolbar_layout.addWidget(self.tridimensional_button)
        toolbar_layout.addStretch(1)
        right_layout.addLayout(toolbar_layout)

        parent_layout.addLayout(right_layout, 5)

    def _setup_signals(self):
        # Route every box’s delta into _apply_state
        for box in self.boxes:
            box.state_changed.connect(self._apply_state)

        self.plot_button.clicked.connect(self._on_plot_clicked)
        self.tridimensional_button.clicked.connect(self._on_3d_toggled)

    def _apply_state(self, delta: dict):
        """
        Apply the incoming partial state (`delta`), update self.state,
        then reconfigure UI and plotting as needed.
        """
        # 1) Merge incoming changes
        if delta:
            logger.info("Applying state delta: %s", delta)
            self.state = self.state.with_updates(**delta)

            # Show/hide second-file button for heterocorrelation
            if "corr_type" in delta:
                is_hetero = (self.state.corr_type is CorrType.HETERO)
                self.boxes[1].file2_button.setVisible(is_hetero)

            # Push the new state into each widget
            for box in self.boxes:
                if hasattr(box, "update_from_state"):
                    box.update_from_state(self.state)

        # 2) If we've already plotted once, handle recompute & redraw
        if self.plot_ready:
            # a) Full recompute when any “recalc” field changed
            if GuiState.requiring_recalc & delta.keys():
                self._recalculate_correlation()

            # b) Redraw 2D plot if we're still in 2D mode
            if not self.state.show_3d:
                self.plotter.plot(
                    shownGraph=self.state.shown_graph.value,
                    **self.get_plot_args()
                )
                self.canvas.draw()

        # 3) Handle toggling into/out of 3D mode
        if {"show_3d", "shown_graph"} & delta.keys():
            self._update_3d_view()

    def _on_plot_clicked(self):
        """Triggered when the user clicks ‘Plot’ for the first time."""
        try:
            # Validate files
            f1, f2 = self.state.filename1, self.state.filename2
            if not f1:
                QMessageBox.warning(self, "Missing File", "Please choose at least one input file.")
                return

            if self.state.corr_type is CorrType.HOMO:
                f2 = f1
            elif not f2:
                QMessageBox.warning(self, "Missing Second File",
                                    "Choose the second file for heterocorrelation or switch to homocorrelation.")
                return

            # Unpack Excel params if needed
            if self.state.format1 == "xlsx" and self.state.excel_params1:
                f1 = (*f1, *self.state.excel_params1)
                if self.state.corr_type is CorrType.HOMO:
                    f2 = f1
            if f2 and self.state.format2 == "xlsx" and self.state.excel_params2:
                f2 = (*f2, *self.state.excel_params2)

            # Build & plot
            self.correlation_model = self.controller.build_model(f1, f2, self.state)
            if not self.correlation_model:
                return

            self.plotter = CorrelationPlotter(model=self.correlation_model,
                                              figure=self.figure, canvas=self.canvas)
            self.plotter.plot(shownGraph=self.state.shown_graph.value, **self.get_plot_args())
            self.plot_ready = True
            logger.info("2D plot generated.")

        except ValueError as ve:
            logger.warning("Validation Error: %s", ve)
            QMessageBox.warning(self, "Validation Error", str(ve))
        except Exception as e:
            logger.exception("Unexpected plotting error")
            QMessageBox.critical(self, "Unexpected Error", str(e))

    def _on_3d_toggled(self, checked: bool):
        """Toggle between 2D and 3D views."""
        if not getattr(self, "correlation_model", None):
            QMessageBox.information(self, "Information", "Generate the 2D plot first.")
            self.tridimensional_button.setChecked(self.state.show_3d)
            return

        # Emit as a normal state change
        self._apply_state({'show_3d': checked})

    def _update_3d_view(self):
        """Switch canvas/toolbars based on self.state.show_3d."""
        if self.state.show_3d:
            which = "sync" if self.state.shown_graph is ShownGraph.SYNC else "async"
            self.backend3d.plot3d(self.correlation_model, self.state.color_map, which=which)
            self.canvas.hide()
            self.toolbar.hide()
            self.webview.show()
            self.tridimensional_button.setText("Show 2D Plot")
            # Force WebGL resize
            self.webview.page().runJavaScript("window.dispatchEvent(new Event('resize'));")
        else:
            self.webview.hide()
            self.toolbar.show()
            self.canvas.show()
            self.tridimensional_button.setText("Show 3D Plot")
            self.canvas.draw()

    def _recalculate_correlation(self):
        """Re-run correlation computation on the existing model."""
        try:
            method = self.state.calc_method.value
            logger.info("Recalculating correlation via %s", method)
            self.correlation_model.syn(method=method)
            self.correlation_model.asyn(method=method)
        except Exception as e:
            logger.exception("Recalculation failed")
            QMessageBox.critical(self, "Calculation Error", str(e))

    def get_plot_args(self) -> dict:
        """Translate our GuiState into keyword args for CorrelationPlotter.plot."""
        return {
            "color_map":             self.state.color_map,
            "num_contours":          self.state.num_contours,
            "locator":               self.state.locator_choice,
            "sync_diag":             self.state.sync_diag.value,
            "async_diag":            self.state.async_diag.value,
            "x_axis":                self.state.x_axis.value,
            "color_map_intensity":   self.state.color_map_intensity,
            "contour_line_color":    self.state.contour_line_color,
            "contour_line_alpha":    self.state.contour_lines_intensity,
            "peaks":                 self.state.peaks_signs.value,
        }

    def get_font_title(self):
        font = QtGui.QFont("Arial", 12)
        font.setBold(True)
        return font

    def get_font_text(self):
        return QtGui.QFont("Arial", 10)
