# tests/test_correlation_math.py
# -*- coding: utf-8 -*-
"""
Tests for TwoDCorrelation in correlation_math.py:
- __init__: spec2 duplication and describe frames
- noda: correct hilbert weight matrix
- sync: HT and FFT methods on zero input
- async_: HT on identity input, FFT on zero input
"""
import numpy as np
import pandas as pd
import pytest
from py2dcos.core.math.correlation_math import TwoDCorrelation
from py2dcos.config.resources import CalcMethod

@pytest.fixture
def zero_df():
    # 2 rows × 3 columns of zeros
    return pd.DataFrame(np.zeros((2, 3)), index=['r1', 'r2'], columns=['c1', 'c2', 'c3'])

@pytest.fixture
def identity_df():
    # 2×2 identity matrix, rows and cols named 'r1','r2' and 'c1','c2'
    return pd.DataFrame([[1, 0], [0, 1]], index=['r1', 'r2'], columns=['c1', 'c2'])

def test_init_spec2_copy_and_describe(zero_df):
    # spec2 should be a copy when not provided
    corr = TwoDCorrelation(zero_df)
    assert corr.spec2 is not zero_df
    pd.testing.assert_frame_equal(corr.spec2, zero_df)
    # describe1 and describe2 should match
    pd.testing.assert_frame_equal(corr.describe1, corr.describe2)

    # when spec2 provided, it should not be duplicated
    custom = pd.DataFrame([[1, 2, 3]], index=['r'], columns=['a', 'b', 'c'])
    corr2 = TwoDCorrelation(custom, custom)
    assert corr2.spec2 is custom
    pd.testing.assert_frame_equal(corr2.describe1, corr2.describe2)

def test_noda_nn2():
    # For nn=2, noda matrix should be [[0, 1/π], [-1/π, 0]]
    df = pd.DataFrame([[0, 0]], index=['r'], columns=['x', 'y'])
    corr = TwoDCorrelation(df)
    noda = corr.noda()
    expected = np.array([[0.0, 1/np.pi], [-1/np.pi, 0.0]], dtype=float)
    np.testing.assert_allclose(noda, expected, atol=1e-8)

def test_sync_ht_zero(zero_df):
    corr = TwoDCorrelation(zero_df, zero_df)
    result = corr.sync(method=CalcMethod.HT)
    # zeros input → zeros output, shape = (2,2)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 2)
    assert np.all(result.values == 0.0)

def test_sync_fft_zero(zero_df):
    corr = TwoDCorrelation(zero_df)
    result = corr.sync(method=CalcMethod.FFT)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 2)
    assert np.allclose(result.values, 0.0)

def test_async_ht_identity(identity_df):
    corr = TwoDCorrelation(identity_df)
    result = corr.async_(method=CalcMethod.HT)
    # expected asynchronous HT = noda() matrix, indexed by rows
    noda = corr.noda()
    expected_df = pd.DataFrame(noda, index=identity_df.index, columns=identity_df.index)
    pd.testing.assert_frame_equal(result, expected_df)

def test_async_fft_zero(zero_df):
    corr = TwoDCorrelation(zero_df)
    result = corr.async_(method=CalcMethod.FFT)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 2)
    assert np.allclose(result.values, 0.0)
