# src/py2dcos/plotting/backends/base.py

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class PlotBase:
    """
    base class for all 2d plotting backends

    manages a matplotlib figure instance for drawing
    """

    def __init__(self, *, figure: Figure | None = None):
        # use existing figure when embedding in gui, otherwise create new one
        self.figure: Figure = figure or plt.figure()

    # subclasses must implement:
    # def draw(self, model, settings) -> Figure
