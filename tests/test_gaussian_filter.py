import pandas as pd
import numpy as np
from py2dcos.core.filters import apply_gaussian_filter

def create_mock_data(rows=10, cols=20):
    """Create DataFrame with **different** rows so smoothing changes it."""
    rng = np.random.default_rng(seed=42)
    data = rng.random((rows, cols))  # random values vary along both axes
    return pd.DataFrame(data, index=[f"row_{i}" for i in range(rows)],
                               columns=[f"col_{j}" for j in range(cols)])

def test_preserves_shape():
    df = create_mock_data()
    smoothed = apply_gaussian_filter(df, sigma=1)
    assert smoothed.shape == df.shape

def test_values_change_when_sigma_positive():
    df = create_mock_data()
    smoothed = apply_gaussian_filter(df, sigma=1)
    assert not np.allclose(df.values, smoothed.values)

def test_no_change_when_sigma_zero():
    df = create_mock_data()
    smoothed = apply_gaussian_filter(df, sigma=0)
    assert np.allclose(df.values, smoothed.values)
