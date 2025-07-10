from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class PlotBase(ABC):

    # Abstract base for 2D‐plot backends. Owns a Figure.

    def __init__(self, figure: Figure | None = None):
        # Use provided Figure or make a new one
        self.figure = figure if figure is not None else plt.figure()
        # Clear it so every draw starts fresh
        self.figure.clf()

    @abstractmethod
    def draw(self, model, settings):
        pass