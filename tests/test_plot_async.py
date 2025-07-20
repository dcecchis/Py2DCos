# tests/test_plot_async.py
# -*- coding: utf-8 -*-
import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.interpolate import RegularGridInterpolator
from py2dcos.plotting.backends.plot_async import plot_async2d
from py2dcos.config.resources import (
    CANVAS_BACKGROUND, PeaksSigns, Diagonal, AxisDirection
)

class DummyModel:
    """Minimal model with required attributes for plot_async2d."""
    pass

@pytest.fixture
def model_mixed():
    # 2×2 async correlation matrix with positive and negative
    df = pd.DataFrame([[1.0, -1.0], [-2.0, 2.0]],
                      index=[10, 20],
                      columns=[100, 200])
    m = DummyModel()
    m.asyncr = df
    # describe1 and describe2 used only for upper/lefter panels; reuse df.describe
    desc = df.transpose().describe().transpose()
    m.describe1 = desc
    m.describe2 = desc
    m.first1 = df.iloc[:, 0]
    m.last1  = df.iloc[:, -1]
    m.first2 = df.iloc[:, 0]
    m.last2  = df.iloc[:, -1]
    return m

class DummySettings:
    """Dummy PlotSettings-like object with needed attributes."""
    def __init__(self):
        self.locator = 'linear'
        self.num_contours = 5
        self.peaks = PeaksSigns.ALL
        self.color_map = 'viridis'
        self.color_map_intensity = 0.8
        self.contour_line_color = 'black'
        self.contour_line_alpha = 0.5
        self.async_diag = Diagonal.MAIN
        self.x_axis = AxisDirection.DECREASING

def _get_central_ax(fig):
    # central panel has images
    for ax in fig.axes:
        if ax.images:
            return ax
    return None

def test_plot_async2d_basic_figure_and_background(model_mixed):
    settings = DummySettings()
    fig = plot_async2d(model_mixed, settings)
    assert isinstance(fig, plt.Figure)
    # facecolor matches background
    bg = fig.get_facecolor()
    expected = mcolors.to_rgba(CANVAS_BACKGROUND)
    assert bg == expected

def test_plot_async2d_all_peaks_shows_full_data_and_inverted_x(model_mixed):
    settings = DummySettings()
    settings.peaks = PeaksSigns.ALL
    fig = plot_async2d(model_mixed, settings)
    ax = _get_central_ax(fig)
    assert ax is not None
    arr = ax.images[0].get_array()
    # data reversed on first axis: original [[1,-1],[-2,2]] -> [[-2,2],[1,-1]]
    assert np.array_equal(arr, np.array([[-2.0,  2.0],
                                         [ 1.0, -1.0]]))
    # x-axis inverted by default
    assert ax.xaxis_inverted()

def test_plot_async2d_positive_peaks_masks_negatives(model_mixed):
    settings = DummySettings()
    settings.peaks = PeaksSigns.POSITIVE
    fig = plot_async2d(model_mixed, settings)
    ax = _get_central_ax(fig)
    arr = ax.images[0].get_array()
    # only positive entries retained, negatives become nan, reversed rows:
    # model.asyncr.values = [[1,-1],[-2,2]]; mask negatives -> [[1,nan],[nan,2]]; reversed -> [[nan,2],[1,nan]]
    expected = np.array([[np.nan, 2.0],
                         [1.0, np.nan]])
    assert np.allclose(arr, expected, equal_nan=True)

def test_plot_async2d_negative_peaks_masks_positives(model_mixed):
    settings = DummySettings()
    settings.peaks = PeaksSigns.NEGATIVE
    fig = plot_async2d(model_mixed, settings)
    ax = _get_central_ax(fig)
    arr = ax.images[0].get_array()
    # only negative entries retained, positives become nan, reversed:
    # [[1,-1],[-2,2]] -> [[nan,-1],[-2,nan]] -> reversed -> [[-2,nan],[nan,-1]]
    expected = np.array([[-2.0, np.nan],
                         [np.nan, -1.0]])
    assert np.allclose(arr, expected, equal_nan=True)

def test_plot_async2d_contour_collections_present(model_mixed):
    settings = DummySettings()
    fig = plot_async2d(model_mixed, settings)
    ax = _get_central_ax(fig)
    # contour lines are in ax.collections
    assert hasattr(ax, 'collections')
    assert len(ax.collections) > 0

def test_plot_async2d_async_diag_anti_switches_diagonal(model_mixed):
    # Test anti-diagonal overlay path
    settings = DummySettings()
    settings.async_diag = Diagonal.ANTI
    fig = plot_async2d(model_mixed, settings)
    ax = _get_central_ax(fig)
    # After anti diag, central has a Line2D artist overlay
    lines = [ln for ln in ax.lines]
    assert any(len(ln.get_xdata()) > 0 for ln in lines)
