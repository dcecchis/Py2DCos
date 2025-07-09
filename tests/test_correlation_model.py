# tests/test_correlation_model.py
import numpy as np
import pandas as pd
import pytest

from py2dcos.core.correlation_model import CorrelationModel


def _write_csv(df: pd.DataFrame, path):
    # write DataFrame without header so reader uses row 0 as index
    df.to_csv(path, header=False)


def _make_spec(n_rows=30, n_cols=6, seed=0):
    # generate a random spectra-like DataFrame
    rng = np.random.default_rng(seed)
    data = rng.normal(size=(n_rows, n_cols))
    index = np.linspace(4000, 400, n_rows) # IR-like wavenumbers
    cols = [f"p{j}" for j in range(n_cols)]
    return pd.DataFrame(data, index=index, columns=cols)

# Basic construction: fields should build and match expected shapes
def test_model_builds_and_shapes(tmp_path):
    # create two similar spectra files
    spec = _make_spec()
    f1 = tmp_path / "spec1.csv"
    f2 = tmp_path / "spec2.csv"
    _write_csv(spec, f1)
    _write_csv(spec * 1.05, f2)  # slightly different spectra

    # build model with Hilbert transform and no PCA reconstruction    
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
    # synchronous map must be symmetric
    assert np.allclose(model.syncr.values, model.syncr.values.T, atol=1e-12)
    # asynchronous map diagonal should be near zero
    assert np.allclose(np.diag(model.asyncr), 0.0, atol=1e-12)


# Reference-subtraction modes: ensure each works without error

@pytest.mark.parametrize("ref_key", ["mean", "min", "max", "ini", "end"])
def test_reference_modes(tmp_path, ref_key):
    # save a single spectrum for all modes
    spec = _make_spec(seed=1)
    f = tmp_path / "spec.csv"
    _write_csv(spec, f)

    # building with various reference keys should succeed
    model = CorrelationModel([str(f), "csv"], ref=ref_key, reconstruction_comps=0)

    n = spec.shape[0]
    assert model.syncr.shape == (n, n)
    assert model.asyncr.shape == (n, n)


# Filters: Gaussian smoothing and node attenuation 
def test_filters_reduce_average_magnitude(tmp_path):
    base = _make_spec(seed=2)
    f = tmp_path / "spec.csv"
    _write_csv(base, f)

    # model without filters
    m_nominal = CorrelationModel([str(f), "csv"], reconstruction_comps=0)
    power_nominal = m_nominal.core.spec1.abs().values.mean()

    # model with both filters
    m_filtered = CorrelationModel(
        [str(f), "csv"],
        sigma_gaussian=2,
        node_attenuation=True,
        reconstruction_comps=0,
    )
    power_filtered = m_filtered.core.spec1.abs().values.mean()

    # expect at least 5% reduction in average magnitude
    assert power_filtered < power_nominal * 0.95 
