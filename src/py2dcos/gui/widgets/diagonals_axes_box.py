from PyQt5.QtWidgets import QLabel, QRadioButton, QGridLayout, QButtonGroup
from PyQt5.QtCore    import Qt, pyqtSignal
from py2dcos.config.resources import Diagonal, AxisDirection
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.datatypes             import PlotSettings
from .base_box import BaseBox

class DiagonalsAxesBox(BaseBox):
    """
    section for choosing sync/async diagonals and x-axis direction.
    """
    state_changed = pyqtSignal(dict)

    def __init__(self, snapshot: GuiSnapshot, parent=None):
        super().__init__("Diagonals and Axes", snapshot, parent)

        self._buid_ui()
        self._apply_snapshot(snapshot)

        for i in self._controls:
            i.toggled.connect(self._emit_plot)


    def update_from_snapshot(self, snap: GuiSnapshot) -> None:
        # block signals so we don’t trigger handlers while syncing ui controls
        super().update_from_snapshot(snap)
        with self.block_signals(*self._controls):
            self._apply_snapshot(snap)

    def _apply_snapshot(self, snap: GuiSnapshot) -> None:
        self.sync_main .setChecked(snap.plot.sync_diag  is Diagonal.MAIN)
        self.sync_anti .setChecked(snap.plot.sync_diag  is Diagonal.ANTI)
        self.async_main.setChecked(snap.plot.async_diag is Diagonal.MAIN)
        self.async_anti.setChecked(snap.plot.async_diag is Diagonal.ANTI)
        self.x_incr    .setChecked(snap.plot.x_axis    is AxisDirection.INCREASING)
        self.x_decr    .setChecked(snap.plot.x_axis    is AxisDirection.DECREASING)
    
    def _emit_plot(self, checked: bool):
        if not checked:
            return                               # ignore the “off” click

        new_plot = self.snapshot.plot.update(
            sync_diag  = Diagonal.MAIN if self.sync_main.isChecked()  else Diagonal.ANTI,
            async_diag = Diagonal.MAIN if self.async_main.isChecked() else Diagonal.ANTI,
            x_axis     = AxisDirection.INCREASING if self.x_incr.isChecked()
                         else AxisDirection.DECREASING,
        )
        self.state_changed.emit({"plot": new_plot})

    def _buid_ui(self):
        # use grid layout so labels and options align in rows and columns
        grid = QGridLayout()
        #grid.setColumnMinimumWidth(0, 90)
        self.lay.addLayout(grid)


        # row labels for each setting
        grid.addWidget(QLabel("Sync:"),   0, 0)
        grid.addWidget(QLabel("Async:"),  1, 0)
        grid.addWidget(QLabel("X axis:"), 2, 0)

        # create radio buttons for sync diagonal options
        self.sync_main = QRadioButton("main diag")
        self.sync_anti = QRadioButton("antidiag")
        grid.addWidget(self.sync_main, 0, 1)
        grid.addWidget(self.sync_anti, 0, 2)

        # create radio buttons for async diagonal options
        self.async_main = QRadioButton("main diag")
        self.async_anti = QRadioButton("antidiag")
        grid.addWidget(self.async_main, 1, 1)
        grid.addWidget(self.async_anti, 1, 2)

        # create radio buttons for x-axis direction
        self.x_incr = QRadioButton("increasing")
        self.x_decr = QRadioButton("decreasing")
        grid.addWidget(self.x_incr, 2, 1)
        grid.addWidget(self.x_decr, 2, 2)

        # collect all controls to enable signal-blocking during updates
        self._controls = [
            self.sync_main, self.sync_anti,
            self.async_main, self.async_anti,
            self.x_incr, self.x_decr
        ]

        # group related radios so only one can be selected at a time
        self.sdiag_group = QButtonGroup(self)
        self.sdiag_group.addButton(self.sync_main)
        self.sdiag_group.addButton(self.sync_anti)

        self.adiag_group = QButtonGroup(self)
        self.adiag_group.addButton(self.async_main)
        self.adiag_group.addButton(self.async_anti)

        self.xaxis_group = QButtonGroup(self)
        self.xaxis_group.addButton(self.x_incr)
        self.xaxis_group.addButton(self.x_decr)