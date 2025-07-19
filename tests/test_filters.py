# tests/test_filters.py
import numpy as np
import pandas as pd
import pytest

from py2dcos.core.math.filters import apply_gaussian_filter, apply_node_attenuation


def _make_random_spec(n_rows=100, n_cols=4, seed=42):
    # generate random spectra DataFrame
    rng = np.random.default_rng(seed)
    data = rng.normal(loc=0.0, scale=1.0, size=(n_rows, n_cols))
    index = np.linspace(4000, 400, n_rows)  # IR-like wavenumbers
    cols = [f"spec_{i}" for i in range(n_cols)]
    return pd.DataFrame(data, index=index, columns=cols)


# Gaussian filter tests

def test_gaussian_filter_identity_when_sigma_zero():
    # sigma=0 should not alter data
    spec = _make_random_spec()
    out = apply_gaussian_filter(spec, sigma=0)
    pd.testing.assert_frame_equal(out, spec)


def test_gaussian_filter_reduces_variance():
    # sigma>0 should smooth data and lower variance
    spec = _make_random_spec()
    var_before = spec.var().mean()
    out = apply_gaussian_filter(spec, sigma=2)
    var_after = out.var().mean()
    assert var_after < var_before * 0.9  # at least 10 % smoothing


def test_gaussian_filter_preserves_shape_and_index():
    # output must keep same shape and labels
    spec = _make_random_spec()
    out = apply_gaussian_filter(spec, sigma=1)
    assert out.shape == spec.shape
    assert (out.index == spec.index).all()
    assert list(out.columns) == list(spec.columns)


#                            Node-attenuation filter                          #

def test_node_attenuation_identity_on_constant_spectrum():
    # constant input should remain unchanged
    const_spec = pd.DataFrame(
        np.ones((50, 3)),
        index=np.linspace(2000, 1000, 50),
        columns=["a", "b", "c"],
    )
    out = apply_node_attenuation(const_spec)
    pd.testing.assert_frame_equal(out, const_spec)


def test_node_attenuation_applies_rowwise_scalar_factor():
    # each row must be scaled uniformly across columns
    spec = _make_random_spec()
    out = apply_node_attenuation(spec)
    ratios = out.values / spec.values
    row_spread = ratios.max(axis=1) - ratios.min(axis=1)
    assert np.allclose(row_spread, 0.0, atol=1e-12)
