from PyQt5.QtWidgets import QLabel, QRadioButton, QGridLayout, QButtonGroup
from PyQt5.QtCore    import Qt, pyqtSignal
from py2dcos.config.resources import Diagonal, AxisDirection
from .base_box import BaseBox

class DiagonalsAxesBox(BaseBox):
    """
    section for choosing sync/async diagonals and x-axis direction.

    emits state_changed with keys:
      - 'sync_diag': diagonal enum
      - 'async_diag': diagonal enum
      - 'x_axis': axis direction enum
    """
    state_changed = pyqtSignal(dict)

    def __init__(self, state, parent=None):
        super().__init__("Diagonals and Axes", state, parent)

        # use grid layout so labels and options align in rows and columns
        grid = QGridLayout()
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

        # set initial selections to mirror current gui state
        self.sync_main .setChecked(state.sync_diag  is Diagonal.MAIN)
        self.sync_anti .setChecked(state.sync_diag  is Diagonal.ANTI)
        self.async_main.setChecked(state.async_diag is Diagonal.MAIN)
        self.async_anti.setChecked(state.async_diag is Diagonal.ANTI)
        self.x_incr    .setChecked(state.x_axis    is AxisDirection.INCREASING)
        self.x_decr    .setChecked(state.x_axis    is AxisDirection.DECREASING)

        # connect toggles to handlers that emit the appropriate state change
        self.sync_main.toggled.connect(self._on_sync)
        self.sync_anti.toggled.connect(self._on_sync)
        self.async_main.toggled.connect(self._on_async)
        self.async_anti.toggled.connect(self._on_async)
        self.x_incr.toggled.connect(self._on_x_axis)
        self.x_decr.toggled.connect(self._on_x_axis)

    def update_from_state(self, state):
        # block signals so we don’t trigger handlers while syncing ui controls
        with self.block_signals(*self._controls):
            self.sync_main .setChecked(state.sync_diag  is Diagonal.MAIN)
            self.sync_anti .setChecked(state.sync_diag  is Diagonal.ANTI)
            self.async_main.setChecked(state.async_diag is Diagonal.MAIN)
            self.async_anti.setChecked(state.async_diag is Diagonal.ANTI)
            self.x_incr    .setChecked(state.x_axis    is AxisDirection.INCREASING)
            self.x_decr    .setChecked(state.x_axis    is AxisDirection.DECREASING)

    def _on_sync(self, checked: bool):
        # only emit when a button becomes checked to identify the chosen diag
        if checked:
            val = Diagonal.MAIN if self.sync_main.isChecked() else Diagonal.ANTI
            self.state_changed.emit({'sync_diag': val})

    def _on_async(self, checked: bool):
        # emit new async diagonal based on which radio is active
        if checked:
            val = Diagonal.MAIN if self.async_main.isChecked() else Diagonal.ANTI
            self.state_changed.emit({'async_diag': val})

    def _on_x_axis(self, checked: bool):
        # toggle x_axis direction; emit new value when selection changes
        if checked:
            val = AxisDirection.INCREASING if self.x_incr.isChecked() else AxisDirection.DECREASING
            self.state_changed.emit({'x_axis': val})
