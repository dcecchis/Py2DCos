# tests/test_plotting.py
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from pathlib import Path

from py2dcos.core.correlation_model import CorrelationModel
from py2dcos.plotting.correlation_plot import CorrelationPlotter


def _make_spec(n_rows=25, n_cols=4, seed=0):
    rng = np.random.default_rng(seed)
    data = rng.normal(size=(n_rows, n_cols))
    index = np.linspace(4000, 400, n_rows)
    cols = [f"p{j}" for j in range(n_cols)]
    return pd.DataFrame(data, index=index, columns=cols)


def _write_csv(df, p: Path):
    df.to_csv(p, header=False)


def test_plot_returns_figure_and_axes(monkeypatch, tmp_path):
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)
    monkeypatch.chdir(tmp_path)

    f = tmp_path / "spec.csv"
    _write_csv(_make_spec(), f)

    model = CorrelationModel([str(f), "csv"], reconstruction_comps=0)
    plotter = CorrelationPlotter(model)

    fig = plotter.plot(shownGraph="sync")
    if fig is None:                         # some versions return None
        fig = getattr(plotter, "figure", getattr(plotter, "fig", None))
    assert isinstance(fig, Figure)
    assert len(fig.axes) >= 4
