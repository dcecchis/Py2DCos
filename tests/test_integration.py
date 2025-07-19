import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from pathlib import Path

from py2dcos.core.math.correlation_model import CorrelationModel
from py2dcos.plotting.correlation_plot import CorrelationPlotter


# helper to generate synthetic spectra DataFrame
def _synth_spec(n_rows=32, n_cols=6, seed=0):
    rng = np.random.default_rng(seed)
    data = rng.normal(size=(n_rows, n_cols))
    idx  = np.linspace(4000, 400, n_rows)
    cols = [f"p{j}" for j in range(n_cols)]
    return pd.DataFrame(data, index=idx, columns=cols)

# helper to save DataFrame without header for IO tests
def _to_csv(df, path: Path):
    df.to_csv(path, header=False)


def test_full_pipeline(tmp_path, monkeypatch):
    # prevent GUI show calls
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)

    # create two different spectra files
    f1, f2 = tmp_path / "s1.csv", tmp_path / "s2.csv"
    _to_csv(_synth_spec(seed=0), f1)
    _to_csv(_synth_spec(seed=1), f2)      # different spectra

    # run model with filters and HT method
    model = CorrelationModel(
        [str(f1), "csv"],
        [str(f2), "csv"],
        ref="mean",
        method="HT",
        sigma_gaussian=1,
        node_attenuation=True,
        reconstruction_comps=0,
    )

    n = 32
    # coverage: shape and finite values
    assert model.syncr.shape == model.asyncr.shape == (n, n)
    assert np.isfinite(model.syncr.values).all()
    assert np.isfinite(model.asyncr.values).all()

    # if inputs identical, async should be skew-symmetric
    same_input = np.allclose(_synth_spec(seed=0).values,
                             _synth_spec(seed=1).values)
    if same_input:
        assert np.allclose(model.asyncr.values + model.asyncr.values.T, 0.0,
                           atol=1e-6)

    # test plotting for sync, async, and combined modes
    plotter = CorrelationPlotter(model)
    for mode in ("sync", "async", "both"):
        fig = plotter.plot(shownGraph=mode) or getattr(plotter, "figure", None)
        assert isinstance(fig, Figure)
        assert len(fig.axes) >= 4
