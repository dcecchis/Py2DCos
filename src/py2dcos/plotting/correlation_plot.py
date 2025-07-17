# src/py2dcos/plotting/correlation_plot.py

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from py2dcos.core.correlation_model import CorrelationModel
from py2dcos.plotting.manager        import PlotManager
from py2dcos.plotting.settings       import PlotSettings


class CorrelationPlotter:
    # gui hands off a settings dict so we can delegate to plot manager and update the canvas if provided
    
    def __init__(
        self,
        model:   CorrelationModel,
        figure:  Figure | None = None,
        canvas:  FigureCanvasQTAgg | None = None,
    ) -> None:
        # use existing figure for redraws or create a new one for standalone plots
        self.figure = figure or plt.figure()
        # store optional qt canvas to trigger non-blocking redraws in gui
        self.canvas = canvas
        # facade that picks appropriate backend based on mode
        self.manager = PlotManager(model)

    def update_model(self, model: CorrelationModel) -> None:
        """replace the correlation model and reset the plot manager to avoid stale data"""
        self.model = model
        # new manager ensures internal cache is tied to the updated model
        self.manager = PlotManager(model)

    def plot(
        self,
        *,
        shownGraph: str = "both",
        **settings_kwargs,
    ) -> Figure:
        # clear figure to remove previous plots before drawing anew
        self.figure.clear()

        # build settings object from keyword args to pass into manager
        settings = PlotSettings(**settings_kwargs)
        # delegate drawing to the manager, which returns the figure with new content
        fig = self.manager.render(shownGraph.lower(), settings, fig=self.figure)

        # if embedded in a qt canvas, trigger idle draw for responsiveness
        if self.canvas is not None:
            self.canvas.draw_idle()
        else:
            # fallback to blocking show when no canvas is available
            fig.show()

        return fig
