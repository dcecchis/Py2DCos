import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd
import pytest
from pathlib import Path

from py2dcos.core.math.pca_preprocessing import PCAProcessor


def _rand_df(n_rows=30, n_cols=5, seed=0):
    # generate random DataFrame with IR-like index
    rng = np.random.default_rng(seed)
    data = rng.normal(size=(n_rows, n_cols))
    index = np.linspace(4000, 400, n_rows)        # IR-style wavenumbers
    cols = [f"col_{i}" for i in range(n_cols)]
    return pd.DataFrame(data, index=index, columns=cols)


 # Shape preservation and n_components   

def test_reconstruction_keeps_shape_and_index():
    # reconstruction should keep DataFrame structure unchanged
    df = _rand_df()
    proc = PCAProcessor()
    recon = proc.apply(df, n_components=3,
                       plot_correlogram=False,
                       plot_scores=False)
    assert recon.shape == df.shape
    assert (recon.index == df.index).all()
    assert list(recon.columns) == list(df.columns)


def test_n_components_zero_returns_copy():
    # zero components should return a copy identical to input
    df = _rand_df()
    proc = PCAProcessor()
    out = proc.apply(df, n_components=0)
    pd.testing.assert_frame_equal(out, df)
    assert out is not df # ensure it's a new object


# Report & image file outputs

def test_report_and_plots_written(tmp_path):
    # expect report and image files when plotting enabled
    df = _rand_df()
    proc = PCAProcessor()

    report_file = tmp_path / "pca_report.txt"
    corr_file = tmp_path / "corr.png"
    scores_file = tmp_path / "scores.png"

    proc.apply(
        df,
        n_components=2,
        report_filename=str(report_file),
        plot_correlogram=True,
        correlogram_filename=str(corr_file),
        plot_scores=True,
        scores_filename=str(scores_file),
    )

    assert report_file.exists() and report_file.stat().st_size > 0
    for img in (corr_file, scores_file):
        assert img.exists() and img.stat().st_size > 0


def test_no_plot_files_when_disabled(tmp_path):
    # no files should be created if plotting is disabled
    df = _rand_df()
    proc = PCAProcessor()

    corr_file = tmp_path / "corr.png"
    scores_file = tmp_path / "scores.png"

    proc.apply(
        df,
        n_components=2,
        plot_correlogram=False,
        correlogram_filename=str(corr_file),
        plot_scores=False,
        scores_filename=str(scores_file),
    )
    assert not corr_file.exists()
    assert not scores_file.exists()
