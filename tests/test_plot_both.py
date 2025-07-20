# tests/test_plot_both.py
# -*- coding: utf-8 -*-
import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from py2dcos.plotting.backends.plot_both import plot_both2d
from py2dcos.config.resources import CANVAS_BACKGROUND, PeaksSigns, Diagonal, AxisDirection

class DummyModel:
    """Minimal model with required attributes for plot_both2d."""
    pass

@pytest.fixture
def model():
    # 2×2 sync and async matrices
    df_sync = pd.DataFrame([[1.0, -1.0], [2.0, -2.0]],
                           index=[10, 20],
                           columns=[100, 200])
    df_async = pd.DataFrame([[3.0, -3.0], [4.0, -4.0]],
                            index=[10, 20],
                            columns=[100, 200])
    m = DummyModel()
    m.syncr = df_sync
    m.asyncr = df_async
    # stats for upper/lefter panels: use describe transpose
    desc1 = df_sync.transpose().describe().transpose()
    desc2 = df_async.transpose().describe().transpose()
    m.describe1 = desc1
    m.describe2 = desc2
    m.first1 = df_sync.iloc[:, 0]
    m.last1  = df_sync.iloc[:, -1]
    m.first2 = df_async.iloc[:, 0]
    m.last2  = df_async.iloc[:, -1]
    return m

class DummySettings:
    """Dummy PlotSettings-like object with needed attributes."""
    def __init__(self):
        self.locator = 'linear'
        self.num_contours = 4
        self.peaks = PeaksSigns.ALL
        self.color_map = 'viridis'
        self.color_map_intensity = 0.7
        self.contour_line_color = 'blue'
        self.contour_line_alpha = 0.5
        self.sync_diag = Diagonal.MAIN
        self.async_diag = Diagonal.MAIN
        self.x_axis = AxisDirection.DECREASING

def _get_axes_with_images(fig):
    """Return sync and async axes by identifying axes with images."""
    imgs = [(ax, ax.images[0].get_array()) for ax in fig.axes if ax.images]
    # assume first is sync, second is async
    return imgs[0][0], imgs[0][1], imgs[1][0], imgs[1][1]

def test_plot_both2d_basic_returns_figure_and_background(model):
    settings = DummySettings()
    fig = plot_both2d(model, settings)
    assert isinstance(fig, plt.Figure)
    # check facecolor
    bg = fig.get_facecolor()
    assert bg == mcolors.to_rgba(CANVAS_BACKGROUND)
    # two heatmaps (sync and async)
    sync_ax, sync_arr, async_ax, async_arr = _get_axes_with_images(fig)
    # sync reversed first axis: original [[1,-1],[2,-2]] -> [[2,-2],[1,-1]]
    expected_sync = np.array([[2.0, -2.0], [1.0, -1.0]])
    assert np.array_equal(sync_arr, expected_sync)
    # async reversed first axis: [[3,-3],[4,-4]] -> [[4,-4],[3,-3]]
    expected_async = np.array([[4.0, -4.0], [3.0, -3.0]])
    assert np.array_equal(async_arr, expected_async)
    # x-axes should be inverted
    assert sync_ax.xaxis_inverted()
    assert async_ax.xaxis_inverted()

def test_plot_both2d_positive_peaks_masks_negatives(model):
    settings = DummySettings()
    settings.peaks = PeaksSigns.POSITIVE
    fig = plot_both2d(model, settings)
    sync_ax, sync_arr, async_ax, async_arr = _get_axes_with_images(fig)
    # sync mask: only >0, reversed: original [[1,-1],[2,-2]] masks -> [[1,nan],[2,nan]] -> [[2,nan],[1,nan]]
    expected_sync = np.array([[2.0, np.nan], [1.0, np.nan]])
    assert np.allclose(sync_arr, expected_sync, equal_nan=True)
    # async mask: [[3,-3],[4,-4]] -> [[3,nan],[4,nan]] -> [[4,nan],[3,nan]]
    expected_async = np.array([[4.0, np.nan], [3.0, np.nan]])
    assert np.allclose(async_arr, expected_async, equal_nan=True)

def test_plot_both2d_negative_peaks_masks_positives(model):
    settings = DummySettings()
    settings.peaks = PeaksSigns.NEGATIVE
    fig = plot_both2d(model, settings)
    sync_ax, sync_arr, async_ax, async_arr = _get_axes_with_images(fig)
    # sync mask negative: [[1,-1],[2,-2]] -> [[nan,-1],[nan,-2]] -> [[nan,-2],[nan,-1]]
    expected_sync = np.array([[np.nan, -2.0], [np.nan, -1.0]])
    assert np.allclose(sync_arr, expected_sync, equal_nan=True)
    # async mask negative: [[3,-3],[4,-4]] -> [[nan,-3],[nan,-4]] -> [[nan,-4],[nan,-3]]
    expected_async = np.array([[np.nan, -4.0], [np.nan, -3.0]])
    assert np.allclose(async_arr, expected_async, equal_nan=True)

def test_plot_both2d_anti_diagonal_overlay(model):
    settings = DummySettings()
    settings.sync_diag = Diagonal.ANTI
    settings.async_diag = Diagonal.ANTI
    fig = plot_both2d(model, settings)
    sync_ax, _, async_ax, _ = _get_axes_with_images(fig)
    # after anti-diag, both axes should have at least one line overlay
    assert len(sync_ax.lines) > 0
    assert len(async_ax.lines) > 0
