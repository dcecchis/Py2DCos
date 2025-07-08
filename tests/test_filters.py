# tests/test_filters.py
import numpy as np
import pandas as pd
import pytest

from py2dcos.core.filters import apply_gaussian_filter, apply_node_attenuation


def _make_random_spec(n_rows=100, n_cols=4, seed=42):
    rng = np.random.default_rng(seed)
    data = rng.normal(loc=0.0, scale=1.0, size=(n_rows, n_cols))
    index = np.linspace(4000, 400, n_rows)  # wavenumbers (decreasing IR axis)
    cols = [f"spec_{i}" for i in range(n_cols)]
    return pd.DataFrame(data, index=index, columns=cols)


# --------------------------------------------------------------------------- #
#                               Gaussian filter                               #
# --------------------------------------------------------------------------- #

def test_gaussian_filter_identity_when_sigma_zero():
    """sigma=0 (or (0,0)) should leave the spectrum unchanged."""
    spec = _make_random_spec()
    out = apply_gaussian_filter(spec, sigma=0)
    pd.testing.assert_frame_equal(out, spec)


def test_gaussian_filter_reduces_variance():
    """With sigma>0 the overall variance across the DataFrame should drop."""
    spec = _make_random_spec()
    var_before = spec.var().mean()
    out = apply_gaussian_filter(spec, sigma=2)
    var_after = out.var().mean()
    assert var_after < var_before * 0.9  # at least 10 % smoothing


def test_gaussian_filter_preserves_shape_and_index():
    spec = _make_random_spec()
    out = apply_gaussian_filter(spec, sigma=1)
    assert out.shape == spec.shape
    assert (out.index == spec.index).all()
    assert list(out.columns) == list(spec.columns)


# --------------------------------------------------------------------------- #
#                            Node-attenuation filter                          #
# --------------------------------------------------------------------------- #

def test_node_attenuation_identity_on_constant_spectrum():
    """For a flat spectrum the attenuation factor should be 1 → output= input."""
    const_spec = pd.DataFrame(
        np.ones((50, 3)),
        index=np.linspace(2000, 1000, 50),
        columns=["a", "b", "c"],
    )
    out = apply_node_attenuation(const_spec)
    pd.testing.assert_frame_equal(out, const_spec)


def test_node_attenuation_applies_rowwise_scalar_factor():
    """Each row should be scaled by the same factor across all columns."""
    spec = _make_random_spec()
    out = apply_node_attenuation(spec)

    # For every row, ratio out/in should be identical across columns
    ratios = out.values / spec.values
    # Calculate spread within each row
    row_spread = ratios.max(axis=1) - ratios.min(axis=1)
    assert np.allclose(row_spread, 0.0, atol=1e-12)
