# tests/test_plot_sync.py
# -*- coding: utf-8 -*-
import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from py2dcos.plotting.backends.plot_sync import plot_sync2d
from py2dcos.config.resources import CANVAS_BACKGROUND, PeaksSigns, Diagonal, AxisDirection

class DummyModel:
    """Minimal model with required attributes for plot_sync2d."""
    pass

@pytest.fixture
def model_basic():
    # 2×2 correlation matrix
    df = pd.DataFrame([[1, 2], [3, 4]], index=[10, 20], columns=[100, 200])
    m = DummyModel()
    m.syncr = df
    # describe DataFrame: transpose describe transpose yields same shape
    desc = df.transpose().describe().transpose()
    m.describe1 = desc
    m.describe2 = desc
    # first/last series along variables (columns)
    m.first1 = df.iloc[:, 0]
    m.last1  = df.iloc[:, -1]
    m.first2 = df.iloc[:, 0]
    m.last2  = df.iloc[:, -1]
    return m

class DummySettings:
    """Dummy PlotSettings-like object with needed attributes."""
    def __init__(self):
        self.locator = 'linear'
        self.num_contours = 6
        self.peaks = PeaksSigns.ALL
        self.color_map = 'viridis'
        self.color_map_intensity = 1.0
        self.contour_line_color = 'black'
        self.contour_line_alpha = 1.0
        self.sync_diag = Diagonal.MAIN
        self.x_axis = AxisDirection.DECREASING

def test_plot_sync2d_basic_returns_figure_and_background(model_basic):
    settings = DummySettings()
    fig = plot_sync2d(model_basic, settings)
    assert isinstance(fig, plt.Figure)
    # figure facecolor matches CANVAS_BACKGROUND RGBA
    bg = fig.get_facecolor()
    expected = mcolors.to_rgba(CANVAS_BACKGROUND)
    assert bg == expected

def test_plot_sync2d_all_peaks_image_data_and_xaxis_inverted(model_basic):
    settings = DummySettings()
    settings.peaks = PeaksSigns.ALL
    fig = plot_sync2d(model_basic, settings)
    # locate the central axes (the one with an image)
    central_ax = next((ax for ax in fig.axes if ax.images), None)
    assert central_ax is not None
    arr = central_ax.images[0].get_array()
    # original [[1,2],[3,4]] reversed on first axis => [[3,4],[1,2]]
    assert np.array_equal(arr, np.array([[3, 4], [1, 2]]))
    # x-axis should be inverted by default
    assert central_ax.xaxis_inverted()
