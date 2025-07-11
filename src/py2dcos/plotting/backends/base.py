# src/py2dcos/plotting/backends/base.py
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class PlotBase:
    def __init__(self, *, figure: Figure | None = None):
        self.figure: Figure = figure or plt.figure()

    # every concrete subclass implements
    # def draw(self, model, settings) -> Figure:
