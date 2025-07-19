import numpy as np
import pandas as pd
import pytest

from py2dcos.core.math.correlation_math import TwoDCorrelation


def _rand_spec(n_rows=40, n_cols=6, seed=0):
    rng = np.random.default_rng(seed)
    data = rng.normal(size=(n_rows, n_cols))
    index = np.linspace(4000, 400, n_rows)
    cols = [f"p{j}" for j in range(n_cols)]
    return pd.DataFrame(data, index=index, columns=cols)


# Hilbert Transform tests

def test_sync_ht_symmetry_and_shape():
    # sync HT output must be square and symmetric
    spec = _rand_spec()
    corr = TwoDCorrelation(spec)
    syn = corr.sync(method="HT")
    assert syn.shape == (spec.shape[0], spec.shape[0])
    assert np.allclose(syn.values, syn.values.T, atol=1e-12)


def test_async_ht_skewsym_and_diag_zero():
    # async HT output must be skew-symmetric with zero diagonal
    spec = _rand_spec()
    corr = TwoDCorrelation(spec)
    asyn = corr.async_(method="HT")
    n = spec.shape[0]
    assert asyn.shape == (n, n)
    assert np.allclose(np.diag(asyn), 0.0, atol=1e-12)
    assert np.allclose(asyn.values + asyn.values.T, 0.0, atol=1e-12)


# cross-spectra shape checks for both methods

@pytest.mark.parametrize("method", ["HT", "FFT"])
def test_sync_cross_shapes(method):
    # ensure sync cross-correlation handles different row counts
    spec1 = _rand_spec(n_rows=30, seed=1)
    spec2 = _rand_spec(n_rows=45, seed=2)
    corr = TwoDCorrelation(spec1, spec2)
    syn = corr.sync(method=method)
    assert syn.shape == (30, 45)


# dimension-mismatch guard
def test_mismatched_column_count_raises():
    # mismatched column counts should raise ValueError
    spec1 = _rand_spec(n_cols=5, seed=3)
    spec2 = _rand_spec(n_cols=6, seed=4)
    corr = TwoDCorrelation(spec1, spec2)
    with pytest.raises(ValueError):
        corr.sync()
