from __future__ import annotations
from typing import TYPE_CHECKING
import plotly.graph_objs as go
import matplotlib.cm as mplcm
import matplotlib.colors as mcolors
import numpy as np
import plotly.colors as pc  # new
from py2dcos.datatypes.plot_settings import PlotSettings
from py2dcos.config.resources import ShownGraph

if TYPE_CHECKING:
    from py2dcos.core.math.correlation_model import CorrelationModel


def _to_plotly_scale(cmap, n: int | None = None):
    if isinstance(cmap, (list, tuple)):
        return list(cmap)

    if isinstance(cmap, str) and cmap in pc.named_colorscales() and n is None:
        return cmap

    steps = int(n) if n is not None else 256
    m_cmap = mplcm.get_cmap(cmap, steps) if isinstance(cmap, str) else cmap

    positions = np.linspace(0.0, 1.0, steps)
    return [[float(pos), mcolors.to_hex(m_cmap(pos))] for pos in positions]


def plot3d(
        model: CorrelationModel,
        settings: PlotSettings,
        which: ShownGraph
        ):
    df = model.asyncr if which is ShownGraph.ASYNC else model.syncr
    title = "Asynchronous Spectra" if which is ShownGraph.ASYNC else "Synchronous Spectra"

    cmap = settings.color_map
    n = getattr(settings, "n_colors", None)
    if isinstance(cmap, str) and cmap in pc.named_colorscales() and n is None:
        colorscale = cmap
    else:
        colorscale = _to_plotly_scale(cmap, n)

    fig = go.Figure(
        data=[go.Surface(
            x=df.index.values,
            y=df.columns.values,
            z=df.values,
            colorscale=colorscale  # <-- aquí va la variable, no la llamada directa
        )]
    )

    fig.update_layout(
        title=title,
        autosize=True,
        margin=dict(l=10, r=10, b=10, t=40),
        scene=dict(
            xaxis_title="Wavenumber",
            yaxis_title="Wavenumber",
            zaxis_title="Correlation"
        ),
    )
    return fig