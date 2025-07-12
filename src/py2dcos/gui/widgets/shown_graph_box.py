from PyQt5.QtWidgets import QLabel, QRadioButton, QHBoxLayout, QButtonGroup
from PyQt5.QtCore    import Qt

from py2dcos.config.resources import GuiState, ShownGraph, PeaksSigns
from .base_box import BaseBox

class ShownGraphBox(BaseBox):
    """
    Section for choosing which graph to display (sync/async/both) and which peak signs to show.

    Emits state_changed with keys:
      - 'shown_graph': ShownGraph enum
      - 'peaks_signs': PeaksSigns enum
    """
    def __init__(self, state: GuiState, parent=None):
        super().__init__("Shown Graph", state, parent)

        # Graph selection layout
        graph_layout = QHBoxLayout()
        self.sync_graph = QRadioButton("Sync")
        self.async_graph = QRadioButton("Async")
        self.both_graph = QRadioButton("Both")
        graph_layout.addWidget(self.sync_graph)
        graph_layout.addWidget(self.async_graph)
        graph_layout.addWidget(self.both_graph)
        self.lay.addLayout(graph_layout)

        # Group for mutual exclusivity
        self.graph_group = QButtonGroup(self)
        self.graph_group.addButton(self.sync_graph)
        self.graph_group.addButton(self.async_graph)
        self.graph_group.addButton(self.both_graph)
        self.graph_group.setExclusive(True)

        # Peaks signs layout
        signs_layout = QHBoxLayout()
        self.positive = QRadioButton("Positives")
        self.negative = QRadioButton("Negatives")
        self.all_signs = QRadioButton("All")
        signs_layout.addWidget(self.positive)
        signs_layout.addWidget(self.negative)
        signs_layout.addWidget(self.all_signs)
        self.lay.addLayout(signs_layout)

        # Group for peaks signs exclusivity
        self.signs_group = QButtonGroup(self)
        self.signs_group.addButton(self.positive)
        self.signs_group.addButton(self.negative)
        self.signs_group.addButton(self.all_signs)
        self.signs_group.setExclusive(True)

        # Set default selections from state
        current_graph = state.shown_graph
        self.sync_graph.setChecked(current_graph is ShownGraph.SYNC)
        self.async_graph.setChecked(current_graph is ShownGraph.ASYNC)
        self.both_graph.setChecked(current_graph is ShownGraph.BOTH)

        current_signs = state.peaks_signs
        self.positive.setChecked(current_signs is PeaksSigns.POSITIVE)
        self.negative.setChecked(current_signs is PeaksSigns.NEGATIVE)
        self.all_signs.setChecked(current_signs is PeaksSigns.ALL)

        # Connect signals
        self.sync_graph.toggled.connect(self._on_shown_graph)
        self.async_graph.toggled.connect(self._on_shown_graph)
        self.both_graph.toggled.connect(self._on_shown_graph)
        self.positive.toggled.connect(self._on_peaks_signs)
        self.negative.toggled.connect(self._on_peaks_signs)
        self.all_signs.toggled.connect(self._on_peaks_signs)

    def _on_shown_graph(self, checked: bool):
        if not checked:
            return
        if self.sync_graph.isChecked():
            val = ShownGraph.SYNC
        elif self.async_graph.isChecked():
            val = ShownGraph.ASYNC
        else:
            val = ShownGraph.BOTH
        self.state.shown_graph = val
        self.state_changed.emit({'shown_graph': val})

    def _on_peaks_signs(self, checked: bool):
        if not checked:
            return
        if self.positive.isChecked():
            val = PeaksSigns.POSITIVE
        elif self.negative.isChecked():
            val = PeaksSigns.NEGATIVE
        else:
            val = PeaksSigns.ALL
        self.state.peaks_signs = val
        self.state_changed.emit({'peaks_signs': val})
