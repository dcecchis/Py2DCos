# tests/test_plotly_backend.py
# -*- coding: utf-8 -*-
import pytest
import numpy as np
import pandas as pd
import plotly.colors as pc
import plotly.graph_objs as go
from py2dcos.plotting.backends.plotly_backend import _to_plotly_scale, plot3d
from py2dcos.config.resources import ShownGraph


class DummyModel:
    pass


@pytest.fixture
def model():
    df = pd.DataFrame([[1, 2], [3, 4]], index=[10, 20], columns=[100, 200])
    m = DummyModel()
    m.syncr = df
    m.asyncr = df * 2
    return m


class DummySettings:
    def __init__(self, cmap):
        self.color_map = cmap


def test_to_plotly_scale_builtin():
    name = pc.named_colorscales()[0]
    out = _to_plotly_scale(name)
    assert isinstance(out, str)
    assert out == name


@pytest.mark.parametrize("cmap,n", [("jet", 5), ("viridis", 7)])
def test_to_plotly_scale_custom(cmap, n):
    out = _to_plotly_scale(cmap, n=n)
    assert isinstance(out, list)
    assert len(out) == n
    positions = [entry[0] for entry in out]
    assert positions[0] == pytest.approx(0.0)
    assert positions[-1] == pytest.approx(1.0)
    for _, hexcol in out:
        assert isinstance(hexcol, str) and hexcol.startswith("#")


def _assert_colorscale(trace_colorscale, expected):
    if isinstance(trace_colorscale, str):
        assert trace_colorscale == expected
        return

    # normaliza y compara con tolerancia numérica en posiciones
    got = [[float(a), str(b)] for (a, b) in trace_colorscale]
    want = [[float(a), str(b)] for (a, b) in pc.get_colorscale(expected)]

    assert len(got) == len(want)
    for (pg, cg), (pw, cw) in zip(got, want):
        assert pg == pytest.approx(pw, rel=0, abs=1e-12)
        assert cg == cw

def test_plot3d_sync(model):
    expected = pc.named_colorscales()[0]
    settings = DummySettings(expected)
    fig = plot3d(model, settings, ShownGraph.SYNC)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    trace = fig.data[0]
    np.testing.assert_array_equal(trace.x, model.syncr.index.values)
    np.testing.assert_array_equal(trace.y, model.syncr.columns.values)
    np.testing.assert_array_equal(trace.z, model.syncr.values)
    assert fig.layout.title.text == "Synchronous Spectra"
    _assert_colorscale(trace.colorscale, expected)


def test_plot3d_async(model):
    expected = pc.named_colorscales()[0]
    settings = DummySettings(expected)
    fig = plot3d(model, settings, ShownGraph.ASYNC)
    assert isinstance(fig, go.Figure)
    trace = fig.data[0]
    np.testing.assert_array_equal(trace.z, model.asyncr.values)
    assert fig.layout.title.text == "Asynchronous Spectra"
    _assert_colorscale(trace.colorscale, expected)
