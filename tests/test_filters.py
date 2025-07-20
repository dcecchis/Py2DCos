# tests/test_filters.py
# -*- coding: utf-8 -*-
"""
Tests for apply_gaussian_filter and apply_node_attenuation in py2dcos.core.math.filters
"""
import pandas as pd
import numpy as np
import pytest
from py2dcos.core.math.filters import apply_gaussian_filter, apply_node_attenuation

@pytest.fixture
def df_small():
    # 2×3 DataFrame with float index
    return pd.DataFrame([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
                        index=[100.0, 200.0],
                        columns=['a', 'b', 'c'])

def test_gaussian_zero_sigma_returns_same(df_small):
    out = apply_gaussian_filter(df_small, sigma=0)
    # same values
    pd.testing.assert_frame_equal(out, df_small)

def test_gaussian_tuple_sigma_smooths_across_columns(df_small):
    # use tuple to smooth across columns only (rows unchanged)
    # sigma=(0,1) applies smoothing along axis=1
    out = apply_gaussian_filter(df_small, sigma=(0, 1))
    # shape and labels preserved
    assert isinstance(out, pd.DataFrame)
    assert out.shape == df_small.shape
    assert list(out.index) == list(df_small.index)
    assert list(out.columns) == list(df_small.columns)
    # checking that smoothing occurred: some values differ
    assert not np.allclose(out.values, df_small.values)

def test_gaussian_int_sigma_same_as_float(df_small):
    # integer sigma treated same as float
    out_int = apply_gaussian_filter(df_small, sigma=1)
    out_float = apply_gaussian_filter(df_small, sigma=1.0)
    pd.testing.assert_frame_equal(out_int, out_float)

def test_node_attenuation_constant_spec_returns_same():
    # constant spec → zero derivatives → N_filter = 1 → output equals input
    idx = np.array([0.0, 1.0, 2.0])
    # 3 rows × 2 columns of constant value
    df_const = pd.DataFrame(np.full((3, 2), 5.0),
                             index=idx,
                             columns=['x', 'y'])
    out = apply_node_attenuation(df_const, a=10, lam=2, eps=1e-9)
    pd.testing.assert_frame_equal(out, df_const)

def test_node_attenuation_preserves_index_and_columns(df_small):
    out = apply_node_attenuation(df_small)
    # index and columns unchanged
    assert list(out.index) == list(df_small.index)
    assert list(out.columns) == list(df_small.columns)
    # attenuation factors should be <= 1 for non-negative data
    # i.e., output values should not exceed input
    assert np.all(out.values <= df_small.values)
