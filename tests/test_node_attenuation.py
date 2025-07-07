import numpy as np
import pandas as pd
from py2dcos.core.filters import apply_node_attenuation

def create_mock_df(size=10):
    data = np.random.rand(size, size)
    index = np.linspace(400, 400 + size - 1, size)  # mock wavenumbers
    return pd.DataFrame(data, index=index, columns=index)

def test_shape_preserved():
    df = create_mock_df()
    attenuated = apply_node_attenuation(df)
    assert attenuated.shape == df.shape

def test_diagonal_elements_preserved_ratio():
    diag = np.eye(5) * 3
    index = np.linspace(500, 504, 5)
    df = pd.DataFrame(diag, index=index, columns=index)
    attenuated = apply_node_attenuation(df)
    diag_vals = np.diag(attenuated)

    # All diagonal elements should be equal and greater than zero
    assert np.allclose(diag_vals, diag_vals[0])
    assert diag_vals[0] > 0

def test_zero_handling():
    diag = np.eye(5)
    diag[0, 0] = 0
    index = np.linspace(500, 504, 5)
    df = pd.DataFrame(diag, index=index, columns=index)
    attenuated = apply_node_attenuation(df)
    assert np.all(np.isfinite(attenuated.values)), "Output should not contain inf or NaN"
    assert attenuated.iloc[0, 0] == 0
    assert np.all(attenuated.iloc[0, 1:] == 0)
    assert np.all(attenuated.iloc[1:, 0] == 0)
