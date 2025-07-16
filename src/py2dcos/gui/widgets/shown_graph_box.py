from PyQt5.QtWidgets import QRadioButton, QHBoxLayout, QButtonGroup
from PyQt5.QtCore    import pyqtSignal
from py2dcos.config.resources import ShownGraph, PeaksSigns
from .base_box import BaseBox

class ShownGraphBox(BaseBox):
    """
    section for choosing which graph to display (sync/async/both)
    and which peak signs to show.

    emits state_changed with keys:
      - 'shown_graph': showngraph enum
      - 'peaks_signs': peakssigns enum
    """
    # notify main window when user changes graph or peak sign selection
    state_changed = pyqtSignal(dict)

    def __init__(self, state, parent=None):
        # collapse under 'shown graph' header and store initial state
        super().__init__("shown graph", state, parent)

        # arrange graph selection radios in one row for clear comparison
        graph_layout = QHBoxLayout()
        self.sync_graph  = QRadioButton("Sync")
        self.async_graph = QRadioButton("Async")
        self.both_graph  = QRadioButton("Both")
        graph_layout.addWidget(self.sync_graph)
        graph_layout.addWidget(self.async_graph)
        graph_layout.addWidget(self.both_graph)
        self.lay.addLayout(graph_layout)

        # ensure only one graph option can be active at a time
        self.graph_group = QButtonGroup(self)
        for btn in (self.sync_graph, self.async_graph, self.both_graph):
            self.graph_group.addButton(btn)
        self.graph_group.setExclusive(True)

        # arrange peak sign radios in one row so user can toggle visibility
        signs_layout = QHBoxLayout()
        self.positive = QRadioButton("Positives")
        self.negative = QRadioButton("Negatives")
        self.all_signs = QRadioButton("All")
        signs_layout.addWidget(self.positive)
        signs_layout.addWidget(self.negative)
        signs_layout.addWidget(self.all_signs)
        self.lay.addLayout(signs_layout)

        # collect controls for signal-blocking when syncing state
        self._controls = [
            self.sync_graph, self.async_graph, self.both_graph,
            self.positive,   self.negative,    self.all_signs
        ]

        # group peak sign buttons to enforce single selection
        self.signs_group = QButtonGroup(self)
        for btn in (self.positive, self.negative, self.all_signs):
            self.signs_group.addButton(btn)
        self.signs_group.setExclusive(True)

        # initialize radio buttons to reflect current gui state
        current_graph = state.shown_graph
        self.sync_graph .setChecked(current_graph is ShownGraph.SYNC)
        self.async_graph.setChecked(current_graph is ShownGraph.ASYNC)
        self.both_graph .setChecked(current_graph is ShownGraph.BOTH)

        current_signs = state.peaks_signs
        self.positive .setChecked(current_signs is PeaksSigns.POSITIVE)
        self.negative .setChecked(current_signs is PeaksSigns.NEGATIVE)
        self.all_signs.setChecked(current_signs is PeaksSigns.ALL)

        # connect user toggles to handlers that emit the new state
        self.sync_graph.toggled.connect(self._on_shown_graph)
        self.async_graph.toggled.connect(self._on_shown_graph)
        self.both_graph.toggled.connect(self._on_shown_graph)
        self.positive.toggled.connect(self._on_peaks_signs)
        self.negative.toggled.connect(self._on_peaks_signs)
        self.all_signs.toggled.connect(self._on_peaks_signs)

    def update_from_state(self, state):
        # block signals so updating ui does not trigger handlers
        with self.block_signals(*self._controls):
            # sync/async/both selection sync
            self.sync_graph .setChecked(state.shown_graph is ShownGraph.SYNC)
            self.async_graph.setChecked(state.shown_graph is ShownGraph.ASYNC)
            self.both_graph .setChecked(state.shown_graph is ShownGraph.BOTH)
            # positive/negative/all peak signs sync
            self.positive .setChecked(state.peaks_signs is PeaksSigns.POSITIVE)
            self.negative .setChecked(state.peaks_signs is PeaksSigns.NEGATIVE)
            self.all_signs.setChecked(state.peaks_signs is PeaksSigns.ALL)

    def _on_shown_graph(self, checked: bool):
        # only act when a button is turned on to identify new graph choice
        if not checked:
            return
        if self.sync_graph.isChecked():
            val = ShownGraph.SYNC
        elif self.async_graph.isChecked():
            val = ShownGraph.ASYNC
        else:
            val = ShownGraph.BOTH
        # emit minimal payload indicating what changed
        self.state_changed.emit({'shown_graph': val})

    def _on_peaks_signs(self, checked: bool):
        # only act when a button is turned on to identify new peak sign filter
        if not checked:
            return
        if self.positive.isChecked():
            val = PeaksSigns.POSITIVE
        elif self.negative.isChecked():
            val = PeaksSigns.NEGATIVE
        else:
            val = PeaksSigns.ALL
        # notify listeners about updated peak sign preference
        self.state_changed.emit({'peaks_signs': val})
