import numpy as np
import plotly.graph_objs as go
import matplotlib.cm as mplcm
import matplotlib.colors as mcolors
import plotly.colors as pc      # new

def _to_plotly_scale(name: str, n: int = 256):
    # convert a matplotlib colormap into a plotly-compatible scale
    if name in pc.named_colorscales():
        # use built-in plotly scale when available to avoid recomputing
        return name
    # generate rgba values from matplotlib and convert to hex for plotly
    cmap = mplcm.get_cmap(name, n)
    return [
        [i / (n - 1), mcolors.rgb2hex(cmap(i)[:3])]
        for i in range(cmap.N)
    ]

class PlotlyBackend:
    # backend for rendering interactive 3d surface plots in a webview

    def __init__(self, webview):
        # store reference to the qt webview for embedding html output
        self.webview = webview

    def plot3d(self, model, color_map="Viridis", which="sync"):
        # select synchronous or asynchronous data based on user toggle
        df = model.asyncr if which == "sync" else model.asyncr
        title = "Synchronous Spectra" if which == "sync" else "Asynchronous Spectra"

        # build a plotly figure with a surface trace using the correlation matrix
        fig = go.Figure(
            data=[go.Surface(
                x=df.index.values,
                y=df.columns.values,
                z=df.values,
                colorscale=_to_plotly_scale(color_map)
            )]
        )

        # update layout to set titles and margins for an interactive display
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

        # render the figure as html in the embedded webview for interactivity
        self.webview.setHtml(fig.to_html(full_html=False, include_plotlyjs="cdn"))
        return fig
