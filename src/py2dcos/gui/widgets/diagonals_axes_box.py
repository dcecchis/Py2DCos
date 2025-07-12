from PyQt5.QtWidgets import QLabel, QRadioButton, QGridLayout
from PyQt5.QtCore    import Qt

from py2dcos.config.resources import GuiState, Diagonal, AxisDirection
from .base_box import BaseBox

class DiagonalsAxesBox(BaseBox):
    """
    Section for choosing sync/async diagonals and x-axis direction.

    Emits state_changed with keys:
      - 'sync_diag': Diagonal enum
      - 'async_diag': Diagonal enum
      - 'x_axis': AxisDirection enum
    """
    def __init__(self, state: GuiState, parent=None):
        super().__init__("Diagonals and Axes", state, parent)

        # Grid layout
        grid = QGridLayout()
        self.lay.addLayout(grid)

        # Labels
        grid.addWidget(QLabel("Sync:"), 0, 0)
        grid.addWidget(QLabel("Async:"), 1, 0)
        grid.addWidget(QLabel("X Axis:"), 2, 0)

        # Sync diagonal radio buttons
        self.sync_main = QRadioButton("Main Diag")
        self.sync_anti = QRadioButton("Antidiag")
        grid.addWidget(self.sync_main, 0, 1)
        grid.addWidget(self.sync_anti, 0, 2)

        # Async diagonal radio buttons
        self.async_main = QRadioButton("Main Diag")
        self.async_anti = QRadioButton("Antidiag")
        grid.addWidget(self.async_main, 1, 1)
        grid.addWidget(self.async_anti, 1, 2)

        # X axis direction radio buttons
        self.x_incr = QRadioButton("Increasing")
        self.x_decr = QRadioButton("Decreasing")
        grid.addWidget(self.x_incr, 2, 1)
        grid.addWidget(self.x_decr, 2, 2)

        # Set defaults based on state
        self.sync_main.setChecked(state.sync_diag is Diagonal.MAIN)
        self.sync_anti.setChecked(state.sync_diag is Diagonal.ANTI)
        self.async_main.setChecked(state.async_diag is Diagonal.MAIN)
        self.async_anti.setChecked(state.async_diag is Diagonal.ANTI)
        self.x_incr.setChecked(state.x_axis is AxisDirection.INCREASING)
        self.x_decr.setChecked(state.x_axis is AxisDirection.DECREASING)

        # Connect signals
        self.sync_main.toggled.connect(self._on_sync)
        self.sync_anti.toggled.connect(self._on_sync)
        self.async_main.toggled.connect(self._on_async)
        self.async_anti.toggled.connect(self._on_async)
        self.x_incr.toggled.connect(self._on_x_axis)
        self.x_decr.toggled.connect(self._on_x_axis)

    def _on_sync(self, checked: bool):
        if checked:
            val = Diagonal.MAIN if self.sync_main.isChecked() else Diagonal.ANTI
            self.state.sync_diag = val
            self.state_changed.emit({'sync_diag': val})

    def _on_async(self, checked: bool):
        if checked:
            val = Diagonal.MAIN if self.async_main.isChecked() else Diagonal.ANTI
            self.state.async_diag = val
            self.state_changed.emit({'async_diag': val})

    def _on_x_axis(self, checked: bool):
        if checked:
            val = AxisDirection.INCREASING if self.x_incr.isChecked() else AxisDirection.DECREASING
            self.state.x_axis = val
            self.state_changed.emit({'x_axis': val})
