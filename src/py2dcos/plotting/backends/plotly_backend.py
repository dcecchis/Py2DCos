import numpy as np
import plotly.graph_objs as go
import matplotlib.cm as mplcm
import matplotlib.colors as mcolors
import plotly.colors as pc      # NEW

def _to_plotly_scale(name: str, n: int = 256):
    if name in pc.named_colorscales():
        return name
    cmap = mplcm.get_cmap(name, n)
    return [
        [i / (n - 1), mcolors.rgb2hex(cmap(i)[:3])]
        for i in range(cmap.N)
    ]

class PlotlyBackend:
    def __init__(self, webview):
        self.webview = webview

    def plot3d(self, model, color_map="Viridis", which="sync"):
        df = model.syncr if which == "sync" else model.asyncr
        title = "Synchronous Spectra" if which == "sync" else "Asynchronous Spectra"

        fig = go.Figure(
            data=[go.Surface(
                x=df.index.values,
                y=df.columns.values,
                z=df.values,
                colorscale=_to_plotly_scale(color_map)   # keep the helper
            )]
        )

        fig.update_layout(
            title=title,
            autosize=True,                  # NEW
            margin=dict(l=10, r=10, b=10, t=40),
            scene=dict(
                xaxis_title="Wavenumber",
                yaxis_title="Wavenumber",
                zaxis_title="Correlation"
            ),
        )

        self.webview.setHtml(fig.to_html(full_html=False, include_plotlyjs="cdn"))
        return fig
