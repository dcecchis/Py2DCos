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

# configure logger to capture debug and info messages for troubleshooting
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-5s  %(message)s"
)

class MainWindow(QMainWindow):
    """
    main window manages gui state and coordinates plotting and 3d toggling
    """

    def __init__(self) -> None:
        super().__init__()
        # maintain a single state object representing all gui settings
        self.state = GuiState()
        self.plot_ready = False  # tracks if initial plot has been rendered

        self.setWindowTitle("py2dcos")  # give the window a clear title
        self._build_ui()         # lay out widgets, canvas, and webview
        self._setup_signals()    # wire up interactions between widgets

        # core logic controller and web-based 3d backend need webview ready
        self.controller = AppController()
        self.backend3d = PlotlyBackend(webview=self.webview)

        # push default state into all parameter widgets to reflect initial gui
        self._apply_state({})

    def _build_ui(self) -> None:
        # central widget holds a horizontal splitter for panels
        central = QWidget()
        self.setCentralWidget(central)

        splitter = QSplitter(Qt.Horizontal, central)
        central_layout = QHBoxLayout(central)
        central_layout.addWidget(splitter)

        # left side: scrollable container of parameter selection boxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)

        # instantiate each input/config widget with shared state
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
            # use each widget's docstring as tooltip so user sees guidance
            box.setToolTip(box.__doc__ or "")

        # add the plot button centrally, styled as a title font
        self.plot_button = QPushButton(self.tr("Plot"))
        self.plot_button.setFont(self.get_font_title())
        left_layout.addWidget(self.plot_button, alignment=Qt.AlignHCenter)
        left_layout.addStretch()  # push everything to top

        scroll.setWidget(left_container)
        scroll.setMinimumWidth(340)  # ensure parameter panel has a usable width
        splitter.addWidget(scroll)

        # right side: place for 2d canvas and 3d web view
        plot_container = QWidget()
        self._create_plot_area(plot_container)
        splitter.addWidget(plot_container)

        # give more space to plot area relative to parameter panel
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

    def _create_plot_area(self, container: QWidget) -> None:
        # vertical layout: matplotlib canvas on top, then webview, then toolbar
        right_layout = QVBoxLayout(container)

        # create a figure and canvas for 2d plotting
        self.figure = plt.figure()
        self.figure.set_facecolor("#f0f0f0")  # light gray background for contrast
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(self.canvas)

        # create a hidden webview for 3d plotly plotting until toggled
        self.webview = QWebEngineView()
        self.webview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.webview.hide()
        right_layout.addWidget(self.webview)

        # toolbar layout holds matplotlib controls and 3d toggle button
        tool_layout = QHBoxLayout()
        tool_layout.addStretch()

        self.toolbar = NavigationToolbar(self.canvas, parent=self)
        self.toolbar.setToolTip(self.tr("Pan, zoom, and save the 2D plot"))
        tool_layout.addWidget(self.toolbar)

        self.btn_3d = QPushButton(self.tr("Show 3D plot"))
        self.btn_3d.setCheckable(True)  # allow toggle behavior
        self.btn_3d.setToolTip(self.tr("Toggle between 2D and 3D views"))
        tool_layout.addWidget(self.btn_3d)

        tool_layout.addStretch()
        right_layout.addLayout(tool_layout)

    def _setup_signals(self) -> None:
        # connect each parameter box change to state update logic
        for box in self.boxes:
            box.state_changed.connect(self._apply_state)
        # connect plot and 3d toggle buttons to their handlers
        self.plot_button.clicked.connect(self._on_plot_clicked)
        self.btn_3d.clicked.connect(self._on_3d_toggled)

    def _apply_state(self, delta: dict) -> None:
        """
        merge incoming changes into gui state, update widgets, then
        rebuild or redraw plots and handle 3d toggle if needed
        """
        if delta:
            logger.info("state changed: %s", delta)
            # create a new immutable state reflecting the changes
            self.state = self.state.with_updates(**delta)

            # show or hide second file selector based on correlation type
            if "corr_type" in delta:
                second_box = self.boxes[1]
                second_box.file2_button.setVisible(
                    self.state.corr_type is CorrType.HETERO
                )
            # update each widget so its controls reflect new state
            for box in self.boxes:
                if hasattr(box, "update_from_state"):
                    box.update_from_state(self.state)

        # if a plot is already rendered, decide whether to rebuild data or just redraw
        if self.plot_ready:
            changed_keys = set(delta.keys())
            # heavy changes require full rebuild of correlation model
            if GuiState.requiring_rebuild & changed_keys: # two sets
                self._rebuild_correlation()
            # light changes and not in 3d mode simply redraw 2d
            elif not self.state.show_3d:
                self._redraw_2d()
            else:
                self._update_3d_view()


    def _rebuild_correlation(self) -> None:
        # reconstruct correlation model when inputs or processing options change
        logger.info("rebuilding correlation model…")
        f1, f2 = self.state.filename1, self.state.filename2
        if not f1:
            return  # can't build without at least one file
        if self.state.corr_type is CorrType.HOMO:
            f2 = f1  # use same file for homocorrelation
        
        if self.state.format1 == "xlsx" and self.state.excel_params1:
            f1 = (*f1, *self.state.excel_params1)
            if self.state.corr_type is CorrType.HOMO:
                f2 = f1
        if f2 and self.state.format2 == "xlsx" and self.state.excel_params2:
            f2 = (*f2, *self.state.excel_params2)        

        # controller returns a new model based on file paths and gui state
        self.correlation_model = self.controller.build_model(
            f1, f2, self.state
        )
        # update plotter with new data structure and re-render 2d
        self.plotter.update_model(self.correlation_model)
        self._redraw_2d()

    def _redraw_2d(self) -> None:
        # do nothing if user has switched to 3d view
        if self.state.show_3d:
            return
        # plot data onto existing figure using current plot args
        self.plotter.plot(
            shownGraph=self.state.shown_graph.value,
            **self.get_plot_args()
        )
        # request canvas redraw when idle to optimize performance
        self.canvas.draw_idle()
        logger.debug(
            "redraw complete, max sync value=%.3g",
            self.correlation_model.syncr.values.max()
        )

    def _update_3d_view(self) -> None:
        # switch between 2d canvas and 3d webview based on toggle state
        if self.state.show_3d:
            which = (
                "async" if self.state.shown_graph is ShownGraph.ASYNC
                else "sync"
            )
            # render 3d plot via plotly backend into webview
            self.backend3d.plot3d(
                self.correlation_model,
                self.state.color_map,
                which=which
            )
            # hide 2d elements and show webview for interactive 3d
            self.canvas.hide()
            self.toolbar.hide()
            self.webview.show()
            self.btn_3d.setText("show 2d plot")
            # trigger resize event so webgl canvas adjusts properly
            self.webview.page().runJavaScript(
                "window.dispatchEvent(new Event('resize'));"
            )
        else:
            # revert to 2d: hide webview, show toolbar and canvas again
            self.webview.hide()
            self.toolbar.show()
            self.canvas.show()
            self.btn_3d.setText("show 3d plot")
            self.canvas.draw_idle()

    def _on_plot_clicked(self) -> None:
        """handle initial plot button click: validate inputs, build model, plot"""
        try:
            f1, f2 = self.state.filename1, self.state.filename2
            if not f1:
                # require at least one file before plotting
                QMessageBox.warning(
                    self, "missing file",
                    "please choose at least one input file."
                )
                return
            # ensure second file logic matches correlation type
            if self.state.corr_type is CorrType.HOMO:
                f2 = f1
            elif not f2:
                QMessageBox.warning(
                    self, "missing second file",
                    "choose the second file for heterocorrelation or switch to homocorrelation."
                )
                return

            # expand excel-specific parameters when needed
            if self.state.format1 == "xlsx" and self.state.excel_params1:
                f1 = (*f1, *self.state.excel_params1)
                if self.state.corr_type is CorrType.HOMO:
                    f2 = f1
            if f2 and self.state.format2 == "xlsx" and self.state.excel_params2:
                f2 = (*f2, *self.state.excel_params2)

            # build the correlation model and plotter for the first time
            self.correlation_model = self.controller.build_model(f1, f2, self.state)
            self.plotter = CorrelationPlotter(
                model=self.correlation_model,
                figure=self.figure,
                canvas=self.canvas
            )
            self.plotter.plot(
                shownGraph=self.state.shown_graph.value,
                **self.get_plot_args()
            )
            self.plot_ready = True  # mark that plot exists for future updates
            logger.info("initial 2d plot rendered")
        except Exception as e:
            logger.exception("plot error")
            # show error dialog with exception message for user feedback
            QMessageBox.critical(self, "plot error", str(e))

    def _on_3d_toggled(self, checked: bool) -> None:
        """react to 3d toggle: require existing model then update view state"""
        if not getattr(self, "correlation_model", None):
            # prevent 3d toggle before initial plot exists
            QMessageBox.information(self, "info", "generate the 2d plot first.")
            self.btn_3d.setChecked(self.state.show_3d)
            return
        # re-use state application pipeline for consistency
        self._apply_state({'show_3d': checked})

    def get_plot_args(self) -> dict:
        """collect current gui settings to pass as kwargs into plotter.plot"""
        return {
            'color_map':           self.state.color_map,
            'num_contours':        self.state.num_contours,
            'locator':             self.state.locator_choice,
            'sync_diag':           self.state.sync_diag.value,
            'async_diag':          self.state.async_diag.value,
            'x_axis':              self.state.x_axis.value,
            'color_map_intensity': self.state.color_map_intensity,
            'contour_line_color':  self.state.contour_line_color,
            'contour_line_alpha':  self.state.contour_lines_intensity,
            'peaks':               self.state.peaks_signs.value,
        }

    def get_font_title(self):
        # bold font for section titles or buttons for emphasis
        f = QtGui.QFont("arial", 12)
        f.setBold(True)
        return f

    def get_font_text(self):
        # standard font for labels and paragraph text
        return QtGui.QFont("arial", 10)
