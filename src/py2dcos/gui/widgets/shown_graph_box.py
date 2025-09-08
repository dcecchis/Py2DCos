from PyQt5.QtWidgets import QRadioButton, QHBoxLayout, QButtonGroup
from PyQt5.QtCore    import pyqtSignal
from py2dcos.config.resources import ShownGraph, PeaksSigns
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.datatypes import PlotSettings
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

    def __init__(self, snapshot: GuiSnapshot, parent=None):
        # collapse under 'shown graph' header and store initial state
        super().__init__("Shown graph", snapshot, parent)

        # arrange graph selection radios in one row for clear comparison
        graph_layout = QHBoxLayout()
        self.sync_graph  = QRadioButton("Sync")
        self.async_graph = QRadioButton("Async")
        self.both_graph  = QRadioButton("Both")
        for btn in (self.sync_graph, self.async_graph, self.both_graph):
            graph_layout.addWidget(btn)
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
        for btn in (self.positive, self.negative, self.all_signs):
            signs_layout.addWidget(btn)
        self.lay.addLayout(signs_layout)

        # group peak sign buttons to enforce single selection
        self.signs_group = QButtonGroup(self)
        for btn in (self.positive, self.negative, self.all_signs):
            self.signs_group.addButton(btn)
        self.signs_group.setExclusive(True)

        # collect controls for signal-blocking when syncing state
        self._controls = [
            self.sync_graph, self.async_graph, self.both_graph,
            self.positive,   self.negative,    self.all_signs
        ]

        # initial mirror
        self._apply_snapshot(snapshot)

        # connect GUI → emit
        for rb in self._controls:
            rb.toggled.connect(self._emit_plot)


    def update_from_snapshot(self, snapshot: GuiSnapshot):
        # block signals so updating ui does not trigger handlers
        super().update_from_snapshot(snapshot)
        with self.block_signals(*self._controls):
            self._apply_snapshot(snapshot)

    def _apply_snapshot(self, snapshot: GuiSnapshot):
        p = snapshot.plot
        # sync/async/both selection sync
        self.sync_graph .setChecked(p.shown_graph is ShownGraph.SYNC)
        self.async_graph.setChecked(p.shown_graph is ShownGraph.ASYNC)
        self.both_graph .setChecked(p.shown_graph is ShownGraph.BOTH)
        # positive/negative/all peak signs sync
        self.positive .setChecked(p.peaks is PeaksSigns.POSITIVE)
        self.negative .setChecked(p.peaks is PeaksSigns.NEGATIVE)
        self.all_signs.setChecked(p.peaks is PeaksSigns.ALL)


    def _emit_plot(self, checked: bool):
        if not checked:
            return

        # build new PlotSettings
        p_old = self.snapshot.plot
        p_new = p_old.update(
            shown_graph = (
                ShownGraph.SYNC  if self.sync_graph.isChecked() else
                ShownGraph.ASYNC if self.async_graph.isChecked() else
                                  ShownGraph.BOTH
            ),
            peaks = (
                PeaksSigns.POSITIVE if self.positive.isChecked() else
                PeaksSigns.NEGATIVE if self.negative.isChecked() else
                                     PeaksSigns.ALL
            ),
        )
        self.state_changed.emit({"plot": p_new})