# src/py2dcos/plotting/correlation_plot.py
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from py2dcos.core.correlation_model import CorrelationModel
from py2dcos.plotting.manager        import PlotManager
from py2dcos.plotting.settings       import PlotSettings


class CorrelationPlotter:
    # the GUI passes a ready-made PlotSettings dict. We forward it to PlotManager and refresh the Qt canvas if present.
    
    def __init__(
        self,
        model:   CorrelationModel,
        figure:  Figure | None = None,
        canvas:  FigureCanvasQTAgg | None = None,
    ) -> None:
        self.figure = figure or plt.figure()
        self.canvas = canvas
        self.manager = PlotManager(model)

    def update_model(self, model: CorrelationModel) -> None:
        """Replace the underlying model and reset the PlotManager cache."""
        self.model = model
        self.manager = PlotManager(model)   # ← NEW manager tied to fresh data

    def plot(
        self,
        *,
        shownGraph: str = "both",
        **settings_kwargs,
    ) -> Figure:

        self.figure.clear()

        settings = PlotSettings(**settings_kwargs)
        fig = self.manager.render(shownGraph.lower(), settings, fig=self.figure)

        if self.canvas is not None:
            self.canvas.draw_idle()
        else:
            fig.show()

        return fig