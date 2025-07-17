# src/py2dcos/plotting/manager.py

from py2dcos.plotting.settings import PlotSettings
from py2dcos.plotting.backends.sync2d import Sync2DPlot
from py2dcos.plotting.backends.async2d import Async2DPlot
from py2dcos.plotting.backends.both2d import Both2DPlot
from py2dcos.core.correlation_model import CorrelationModel

class PlotManager:
    """
    facade that picks the right 2d backend based on mode
    renders onto a matplotlib figure and returns it
    """

    def __init__(self, model: CorrelationModel):
        # store the correlation model so backends can pull data for plotting
        self.model = model
        # placeholder for the chosen backend instance
        self._backend = None

    def render(
        self,
        mode: str,               # "sync", "async", or "both"
        settings: PlotSettings,
        fig=None,                # optional existing Figure
    ):
        # map each mode string to its plotting backend class
        mapping = {
            "sync":  Sync2DPlot,
            "async": Async2DPlot,
            "both":  Both2DPlot,
        }
        cls = mapping.get(mode)
        # guard against unsupported modes early to prevent silent failures
        if cls is None:
            raise ValueError(f"unknown plot mode: {mode!r}")

        # instantiate the backend, reusing provided figure if available
        self._backend = cls(figure=fig)
        # delegate drawing to backend and return the resulting figure
        return self._backend.draw(self.model, settings)

    def render3d(self, color_map: str = "coolwarm"):
        # use the backend's 3d plotting method to render interactive view
        self._backend.plot3d(self.model, color_map)
