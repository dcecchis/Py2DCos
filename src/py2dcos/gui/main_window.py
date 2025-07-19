from __future__ import annotations
import logging
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QScrollArea,
    QPushButton, QSizePolicy, QMessageBox, QSplitter, QLabel, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from py2dcos.config.resources import CANVAS_BACKGROUND
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.controller.app_controller import AppController
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
        self.snapshot: GuiSnapshot = GuiSnapshot()
        self.plot_ready = False  # tracks if initial plot has been rendered

        self.figure = plt.figure()
        # core logic controller and web-based 3d backend need webview ready
        self.controller = AppController()
        self.controller.parent_figure = self.figure
        self.controller.busy.connect(self._show_busy)
        self.controller.ready.connect(self._hide_busy)
        self.controller.fig2d_ready.connect(self._show_2d)
        self.controller.fig3d_ready.connect(self._show_3d)
        self.controller.error.connect   (self._show_error)
        self.controller.status_text.connect(self._set_status)
        # push default state into all parameter widgets to reflect initial gui
        self._on_widget_delta({})

        self.setWindowTitle("py2dcos")  # give the window a clear title
        self._build_ui()         # lay out widgets, canvas, and webview
        self._setup_signals()    # wire up interactions between widgets

        self.figure = plt.figure()

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
        self.corr_box   = CorrelationTypeBox(self.snapshot)
        self.input_box  = InputFilesBox(self.snapshot)          # ← keep handle
        self.data_box   = DataTreatmentBox(self.snapshot)
        self.ref_box    = ReferenceSpectraBox(self.snapshot)
        self.graph_box  = GraphSettingsBox(self.snapshot)
        self.diag_box   = DiagonalsAxesBox(self.snapshot)
        self.shown_box  = ShownGraphBox(self.snapshot)

        # put them in a list only for iteration convenience
        self.boxes = [
            self.corr_box,
            self.input_box,
            self.data_box,
            self.ref_box,
            self.graph_box,
            self.diag_box,
            self.shown_box,
        ]
        for box in self.boxes:
            left_layout.addWidget(box)
            box.setToolTip(box.__doc__ or "")

        for box in self.boxes:
            left_layout.addWidget(box)
            # use each widget's docstring as tooltip so user sees guidance
            box.setToolTip(box.__doc__ or "")

        # add the plot button centrally, styled as a title font
        self.plot_button = QPushButton(self.tr("Plot"))
        self.plot_button.setFont(self.get_font_title())
        left_layout.addWidget(self.plot_button, alignment=Qt.AlignHCenter)
        self.status_label = QLabel("")
        self.status_label.hide()               # invisible at start
        left_layout.addWidget(self.status_label, alignment=Qt.AlignHCenter)
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
        self.figure.set_facecolor(CANVAS_BACKGROUND)  # light gray background for contrast
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
            box.state_changed.connect(self._on_widget_delta)
        # connect plot and 3d toggle buttons to their handlers
        self.plot_button.clicked.connect(    lambda: self._on_widget_delta({}, force=True))
        self.btn_3d.clicked.connect(    lambda checked: self._on_widget_delta({'show_3d': checked}))

    def _on_widget_delta(self, delta: dict, *, force=False) -> None:
        """
        delta comes straight from any widget.  Keys are
            'file1' / 'file2'         -> InputFile
            'math'                    -> MathSettings
            'plot'                    -> PlotSettings
            'corr_type'               -> CorrType
            'show_3d'                 -> bool   (3-D toggle)
        """
        if not delta and not force:
            return

        self.snapshot = self.snapshot.update(**delta)
        logger.info("snapshot updated: %s", delta)

        for box in self.boxes:
            box.update_from_snapshot(self.snapshot)

        if 'show_3d' in delta:
            is_3d = self.snapshot.show_3d

            # toggle button
            self.btn_3d.setChecked(is_3d)
            self.btn_3d.setText("Show 2D" if is_3d else "Show 3D")

            # show / hide render areas
            self.canvas.setVisible(not is_3d)
            self.toolbar.setVisible(not is_3d)
            self.webview.setVisible(is_3d)

        self.controller.update_snapshot(self.snapshot, force=force)

    def _show_2d(self, fig):
        self.canvas.draw_idle()

    def _show_3d(self, fig):
        html = fig.to_html(include_plotlyjs="cdn", full_html=False)
        self.webview.setHtml(html)
        self.btn_3d.setChecked(True)

    def _show_error(self, msg: str):
        QMessageBox.critical(self, "Py2DCoS error", msg)

    def _set_status(self, text: str):
        self.status_label.setText(text)
        self.status_label.show()

    def get_font_title(self):
        # bold font for section titles or buttons for emphasis
        f = QtGui.QFont("arial", 12)
        f.setBold(True)
        return f

    def get_font_text(self):
        # standard font for labels and paragraph text
        return QtGui.QFont("arial", 10)

    def _show_busy(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.plot_button.setEnabled(False)
        self.btn_3d      .setEnabled(False)
        self.status_label.setText("Re-calculating…")
        QApplication.processEvents()

    def _hide_busy(self):
        QApplication.restoreOverrideCursor()
        self.plot_button.setEnabled(True)
        self.btn_3d      .setEnabled(True)
        self.status_label.setText("Ready")
