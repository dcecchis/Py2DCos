from PyQt5.QtWidgets import QLabel, QRadioButton, QGridLayout, QButtonGroup
from PyQt5.QtCore    import Qt, pyqtSignal
from py2dcos.config.resources import Diagonal, AxisDirection
from .base_box import BaseBox


class DiagonalsAxesBox(BaseBox):
    """
    Section for choosing sync/async diagonals and x-axis direction.

    Emits state_changed with keys:
      - 'sync_diag': Diagonal enum
      - 'async_diag': Diagonal enum
      - 'x_axis': AxisDirection enum
    """
    # Signal to notify MainWindow of state changes
    state_changed = pyqtSignal(dict)

    def __init__(self, state, parent=None):
        super().__init__("Diagonals and Axes", state, parent)

        # Grid layout
        grid = QGridLayout()
        self.lay.addLayout(grid)

        # Labels for each section
        grid.addWidget(QLabel("Sync:"),   0, 0)
        grid.addWidget(QLabel("Async:"),  1, 0)
        grid.addWidget(QLabel("X Axis:"), 2, 0)

        # Sync diagonal options
        self.sync_main = QRadioButton("Main Diag")
        self.sync_anti = QRadioButton("Antidiag")
        grid.addWidget(self.sync_main, 0, 1)
        grid.addWidget(self.sync_anti, 0, 2)

        # Async diagonal options
        self.async_main = QRadioButton("Main Diag")
        self.async_anti = QRadioButton("Antidiag")
        grid.addWidget(self.async_main, 1, 1)
        grid.addWidget(self.async_anti, 1, 2)

        # X-axis direction options
        self.x_incr = QRadioButton("Increasing")
        self.x_decr = QRadioButton("Decreasing")
        grid.addWidget(self.x_incr, 2, 1)
        grid.addWidget(self.x_decr, 2, 2)

        self._controls = [
            self.sync_main, self.sync_anti,
            self.async_main, self.async_anti,
            self.x_incr, self.x_decr
            ]
        
        # Exclusive groups
        self.sdiag_group = QButtonGroup(self)
        self.adiag_group = QButtonGroup(self)
        self.xaxis_group = QButtonGroup(self)

        # sync diag group
        self.sdiag_group.addButton(self.sync_main)
        self.sdiag_group.addButton(self.sync_anti)

        # async diag group
        self.adiag_group.addButton(self.async_main)
        self.adiag_group.addButton(self.async_anti)

        # x axis
        self.xaxis_group.addButton(self.x_incr)
        self.xaxis_group.addButton(self.x_decr)

        # Initialize selections based on passed-in state
        self.sync_main.setChecked(state.sync_diag is Diagonal.MAIN)
        self.sync_anti.setChecked(state.sync_diag is Diagonal.ANTI)
        self.async_main.setChecked(state.async_diag is Diagonal.MAIN)
        self.async_anti.setChecked(state.async_diag is Diagonal.ANTI)
        self.x_incr.setChecked(state.x_axis is AxisDirection.INCREASING)
        self.x_decr.setChecked(state.x_axis is AxisDirection.DECREASING)

        # Connect UI signals to handlers
        self.sync_main.toggled.connect(self._on_sync)
        self.sync_anti.toggled.connect(self._on_sync)
        self.async_main.toggled.connect(self._on_async)
        self.async_anti.toggled.connect(self._on_async)
        self.x_incr.toggled.connect(self._on_x_axis)
        self.x_decr.toggled.connect(self._on_x_axis)


    def update_from_state(self, state):
        with self.block_signals(*self._controls):
            self.sync_main .setChecked(state.sync_diag  is Diagonal.MAIN)
            self.sync_anti .setChecked(state.sync_diag  is Diagonal.ANTI)
            self.async_main.setChecked(state.async_diag is Diagonal.MAIN)
            self.async_anti.setChecked(state.async_diag is Diagonal.ANTI)
            self.x_incr    .setChecked(state.x_axis    is AxisDirection.INCREASING)
            self.x_decr    .setChecked(state.x_axis    is AxisDirection.DECREASING)

    def _on_sync(self, checked: bool):
        if checked:
            val = Diagonal.MAIN if self.sync_main.isChecked() else Diagonal.ANTI
            self.state_changed.emit({'sync_diag': val})

    def _on_async(self, checked: bool):
        if checked:
            val = Diagonal.MAIN if self.async_main.isChecked() else Diagonal.ANTI
            self.state_changed.emit({'async_diag': val})

    def _on_x_axis(self, checked: bool):
        if checked:
            val = AxisDirection.INCREASING if self.x_incr.isChecked() else AxisDirection.DECREASING
            self.state_changed.emit({'x_axis': val})
