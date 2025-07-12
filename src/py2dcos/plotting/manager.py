# src/py2dcos/plotting/manager.py

from py2dcos.plotting.settings import PlotSettings
from py2dcos.plotting.backends.sync2d import Sync2DPlot
from py2dcos.plotting.backends.async2d import Async2DPlot
from py2dcos.plotting.backends.both2d import Both2DPlot
from py2dcos.core.correlation_model import CorrelationModel

class PlotManager:
    """
    Facade that picks the right 2D backend based on mode,
    renders onto a Matplotlib Figure, and returns it.
    """

    def __init__(self, model: CorrelationModel):
        self.model = model
        self._backend = None

    def render(
        self,
        mode: str,               # "sync", "async", or "both"
        settings: PlotSettings,
        fig=None,                # optional existing Figure
    ):
        # choose backend class
        mapping = {
            "sync":  Sync2DPlot,
            "async": Async2DPlot,
            "both":  Both2DPlot,
        }
        cls = mapping.get(mode)
        if cls is None:
            raise ValueError(f"Unknown plot mode: {mode!r}")

        # instantiate backend with the provided Figure (if any)
        self._backend = cls(figure=fig)
        # draw and return the Figure
        return self._backend.draw(self.model, settings)

    def render3d(self, color_map: str = "coolwarm"):
        self._backend.plot3d(self.model, color_map)
