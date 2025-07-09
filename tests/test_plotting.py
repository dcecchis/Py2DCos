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
    # create random spectra DataFrame
    rng = np.random.default_rng(seed)
    data = rng.normal(size=(n_rows, n_cols))
    index = np.linspace(4000, 400, n_rows)
    cols = [f"p{j}" for j in range(n_cols)]
    return pd.DataFrame(data, index=index, columns=cols)


def _write_csv(df, p: Path):
    # save DataFrame without header for reader compatibility
    df.to_csv(p, header=False)


def test_plot_returns_figure_and_axes(monkeypatch, tmp_path):
    # disable interactive show and work in tmp directory
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)
    monkeypatch.chdir(tmp_path)

    # write a sample spec file
    f = tmp_path / "spec.csv"
    _write_csv(_make_spec(), f)

    # build model and plotter
    model = CorrelationModel([str(f), "csv"], reconstruction_comps=0)
    plotter = CorrelationPlotter(model)

    # attempt to plot and retrieve Figure
    fig = plotter.plot(shownGraph="sync")
    if fig is None:                         
        fig = getattr(plotter, "figure", getattr(plotter, "fig", None))
    # verify it's a matplotlib Figure with subplots
    assert isinstance(fig, Figure)
    assert len(fig.axes) >= 4
