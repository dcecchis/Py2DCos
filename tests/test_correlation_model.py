# tests/test_correlation_model.py
import numpy as np
import pandas as pd
import pytest

from py2dcos.core.correlation_model import CorrelationModel


def _write_csv(df: pd.DataFrame, path):
    # Save without header so io.reader treats row-0 as index
    df.to_csv(path, header=False)


def _make_spec(n_rows=30, n_cols=6, seed=0):
    rng = np.random.default_rng(seed)
    data = rng.normal(size=(n_rows, n_cols))
    index = np.linspace(4000, 400, n_rows)          # IR-like wavenumbers
    cols = [f"p{j}" for j in range(n_cols)]
    return pd.DataFrame(data, index=index, columns=cols)


# --------------------------------------------------------------------------- #
#                              Basic construction                              #
# --------------------------------------------------------------------------- #

def test_model_builds_and_shapes(tmp_path):
    spec = _make_spec()
    f1 = tmp_path / "spec1.csv"
    f2 = tmp_path / "spec2.csv"
    _write_csv(spec, f1)
    _write_csv(spec * 1.05, f2)  # slightly different spectra

    model = CorrelationModel(
        [str(f1), "csv"],
        [str(f2), "csv"],
        ref="zero",
        method="HT",
        reconstruction_comps=0,
    )

    n = spec.shape[0]
    assert model.syncr.shape == (n, n)
    assert model.asyncr.shape == (n, n)
    # Sync map must be symmetric for identical row counts
    assert np.allclose(model.syncr.values, model.syncr.values.T, atol=1e-12)
    # Async diagonal ≈ 0
    assert np.allclose(np.diag(model.asyncr), 0.0, atol=1e-12)


# --------------------------------------------------------------------------- #
#                     Reference-subtraction variants work                      #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("ref_key", ["mean", "min", "max", "ini", "end"])
def test_reference_modes(tmp_path, ref_key):
    spec = _make_spec(seed=1)
    f = tmp_path / "spec.csv"
    _write_csv(spec, f)

    # Single file path is accepted for both spectra
    model = CorrelationModel([str(f), "csv"], ref=ref_key, reconstruction_comps=0)

    # Just ensure successful build and expected square shapes
    n = spec.shape[0]
    assert model.syncr.shape == (n, n)
    assert model.asyncr.shape == (n, n)


# --------------------------------------------------------------------------- #
#                Gaussian + node-attenuation reduce overall power             #
# --------------------------------------------------------------------------- #

def test_filters_reduce_average_magnitude(tmp_path):
    base = _make_spec(seed=2)
    f = tmp_path / "spec.csv"
    _write_csv(base, f)

    # Model without filters
    m_nominal = CorrelationModel([str(f), "csv"], reconstruction_comps=0)
    power_nominal = m_nominal.core.spec1.abs().values.mean()

    # Model with both filters
    m_filtered = CorrelationModel(
        [str(f), "csv"],
        sigma_gaussian=2,
        node_attenuation=True,
        reconstruction_comps=0,
    )
    power_filtered = m_filtered.core.spec1.abs().values.mean()

    assert power_filtered < power_nominal * 0.95  # ≥ 5 % reduction indicates filtering
