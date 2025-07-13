# src/py2dcos/gui/main_window.py

from __future__ import annotations
import logging
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QScrollArea,
    QPushButton, QSizePolicy, QMessageBox, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)

from py2dcos.config.resources import CorrType, ShownGraph
from py2dcos.gui.state import GuiState
from py2dcos.controller.app_controller import AppController
from py2dcos.plotting.backends.plotly_backend import PlotlyBackend
from py2dcos.plotting.correlation_plot import CorrelationPlotter
from py2dcos.gui.widgets import (
    CorrelationTypeBox, InputFilesBox, DataTreatmentBox,
    ReferenceSpectraBox, GraphSettingsBox, DiagonalsAxesBox,
    ShownGraphBox
)

# ----------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-5s  %(message)s"
)

# ----------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """
    Main application window: owns immutable GuiState, receives deltas from widgets,
    orchestrates model rebuild/redraw or style-only redraw, and handles 3D toggling.
    """

    def __init__(self) -> None:
        super().__init__()
        self.state = GuiState()
        self.plot_ready = False

        self.setWindowTitle("Py2DCoS")
        self._build_ui()
        self._setup_signals()

        # Core controller and 3D backend
        self.controller = AppController()
        self.backend3d  = PlotlyBackend(webview=self.webview)

        # Push initial state into widgets
        self._apply_state({})

    # UI construction
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        # Use QSplitter so panels can be resized by the user
        splitter = QSplitter(Qt.Horizontal, central)
        central_layout = QHBoxLayout(central)
        central_layout.addWidget(splitter)

        # ── Left panel: parameter boxes ───────────────────────────────────────
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
            # show a tooltip based on its docstring
            box.setToolTip(box.__doc__ or "")

        self.plot_button = QPushButton(self.tr("Plot"))
        self.plot_button.setFont(self.get_font_title())
        self.plot_button.setToolTip(self.tr(
            "Compute and draw the 2D correlation spectrum"
        ))
        left_layout.addWidget(self.plot_button, alignment=Qt.AlignHCenter)
        left_layout.addStretch()

        scroll.setWidget(left_container)
        scroll.setMinimumWidth(340)
        splitter.addWidget(scroll)

        # ── Right panel: plotting area ──────────────────────────────────────
        plot_container = QWidget()
        self._create_plot_area(plot_container)
        splitter.addWidget(plot_container)

        splitter.setStretchFactor(0, 2)  # left panel: 2 parts
        splitter.setStretchFactor(1, 3)  # right panel: 3/4

    def _create_plot_area(self, container: QWidget) -> None:
        right_layout = QVBoxLayout(container)

        # Matplotlib canvas
        self.figure = plt.figure()
        self.figure.set_facecolor("#f0f0f0")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(self.canvas)

        # Plotly/WebEngine view for 3D
        self.webview = QWebEngineView()
        self.webview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.webview.hide()
        right_layout.addWidget(self.webview)

        # Toolbar + 3D toggle
        tool_layout = QHBoxLayout()
        tool_layout.addStretch()

        self.toolbar = NavigationToolbar(self.canvas, parent=self)
        self.toolbar.setToolTip(self.tr("Pan, zoom, and save the 2D plot"))
        tool_layout.addWidget(self.toolbar)

        self.btn_3d = QPushButton(self.tr("Show 3D Plot"))
        self.btn_3d.setCheckable(True)
        self.btn_3d.setToolTip(self.tr("Toggle between 2D and 3D views"))
        tool_layout.addWidget(self.btn_3d)

        tool_layout.addStretch()
        right_layout.addLayout(tool_layout)

    def _setup_signals(self) -> None:
        for box in self.boxes:
            box.state_changed.connect(self._apply_state)
        self.plot_button.clicked.connect(self._on_plot_clicked)
        self.btn_3d.clicked.connect(self._on_3d_toggled)

    # ------------------------------------------------------------------------
    # State application logic
    # ------------------------------------------------------------------------

    def _apply_state(self, delta: dict) -> None:
        """
        Merge an incoming delta into GuiState, refresh widgets,
        then rebuild or redraw as needed, and handle 3D toggling.
        """
        # 1) Merge state + update widgets
        if delta:
            logger.info("Δ %s", delta)
            self.state = self.state.with_updates(**delta)

            if "corr_type" in delta:
                # toggle second-file button for heterocorrelation
                self.boxes[1].file2_button.setVisible(
                    self.state.corr_type is CorrType.HETERO
                )

            for box in self.boxes:
                if hasattr(box, "update_from_state"):
                    box.update_from_state(self.state)

        # 2) If plot exists, rebuild or style-redraw
        if self.plot_ready:
            changed = set(delta.keys())

            # A) heavy change → full rebuild + redraw
            if GuiState.requiring_rebuild & changed:
                self._rebuild_correlation()

            # B) style-only → redraw 2D
            elif not self.state.show_3d:
                self._redraw_2d()

        # 3) Handle 3D toggle or graph type change
        if {"show_3d", "shown_graph"} & set(delta.keys()):
            self._update_3d_view()

    # ------------------------------------------------------------------------
    # Build / redraw helpers
    # ------------------------------------------------------------------------

    def _rebuild_correlation(self) -> None:
        """Build a new CorrelationModel and redraw the 2D plot."""
        logger.info("Rebuilding correlation model …")
        f1, f2 = self.state.filename1, self.state.filename2
        if not f1:
            return
        if self.state.corr_type is CorrType.HOMO:
            f2 = f1

        self.correlation_model = self.controller.build_model(
            f1, f2, self.state
        )
        self.plotter.update_model(self.correlation_model)
        self._redraw_2d()

    def _redraw_2d(self) -> None:
        """Redraw the 2D plot in the current figure/canvas."""
        if self.state.show_3d:
            return

        self.plotter.plot(
            shownGraph=self.state.shown_graph.value,
            **self.get_plot_args()
        )
        self.canvas.draw_idle()
        logger.debug("Redraw syn max %.3g", self.correlation_model.syncr.values.max())

    def _update_3d_view(self) -> None:
        """Switch between 2D and 3D views based on state.show_3d."""
        if self.state.show_3d:
            which = (
                "sync" if self.state.shown_graph is ShownGraph.SYNC
                else "async"
            )
            self.backend3d.plot3d(
                self.correlation_model,
                self.state.color_map,
                which=which
            )
            self.canvas.hide()
            self.toolbar.hide()
            self.webview.show()
            self.btn_3d.setText("Show 2D Plot")
            # ensure WebGL resizes correctly
            self.webview.page().runJavaScript(
                "window.dispatchEvent(new Event('resize'));"
            )
        else:
            self.webview.hide()
            self.toolbar.show()
            self.canvas.show()
            self.btn_3d.setText("Show 3D Plot")
            self.canvas.draw_idle()

    # ------------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------------

    def _on_plot_clicked(self) -> None:
        """Initial build of the model and first 2D plot."""
        try:
            f1, f2 = self.state.filename1, self.state.filename2
            if not f1:
                QMessageBox.warning(self, "Missing File",
                                    "Please choose at least one input file.")
                return

            if self.state.corr_type is CorrType.HOMO:
                f2 = f1
            elif not f2:
                QMessageBox.warning(
                    self, "Missing Second File",
                    "Choose the second file for heterocorrelation "
                    "or switch to homocorrelation."
                )
                return

            # unpack Excel params if needed
            if self.state.format1 == "xlsx" and self.state.excel_params1:
                f1 = (*f1, *self.state.excel_params1)
                if self.state.corr_type is CorrType.HOMO:
                    f2 = f1
            if f2 and self.state.format2 == "xlsx" and self.state.excel_params2:
                f2 = (*f2, *self.state.excel_params2)

            # build model & plot
            self.correlation_model = self.controller.build_model(
                f1, f2, self.state
            )
            self.plotter = CorrelationPlotter(
                model=self.correlation_model,
                figure=self.figure,
                canvas=self.canvas
            )
            self.plotter.plot(
                shownGraph=self.state.shown_graph.value,
                **self.get_plot_args()
            )
            self.plot_ready = True
            logger.info("Initial 2D plot rendered.")
        except Exception as e:
            logger.exception("Plot error")
            QMessageBox.critical(self, "Plot Error", str(e))

    def _on_3d_toggled(self, checked: bool) -> None:
        """Toggle between 2D and 3D views when the 3D button is clicked."""
        if not getattr(self, "correlation_model", None):
            QMessageBox.information(self, "Info", "Generate the 2D plot first.")
            self.btn_3d.setChecked(self.state.show_3d)
            return
        # reuse the same apply_state pipeline
        self._apply_state({'show_3d': checked})

    # ------------------------------------------------------------------------
    # Plot argument helper & fonts
    # ------------------------------------------------------------------------

    def get_plot_args(self) -> dict:
        """Translate GuiState into kwargs for CorrelationPlotter.plot."""
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
        f = QtGui.QFont("Arial", 12)
        f.setBold(True)
        return f

    def get_font_text(self):
        return QtGui.QFont("Arial", 10)
