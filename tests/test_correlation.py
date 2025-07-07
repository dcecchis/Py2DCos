import pandas as pd
import numpy as np
from py2dcos.core.correlation import TwoDCorrelation

def test_sync_basic():
    df = pd.DataFrame(np.eye(5), index=[1,2,3,4,5])
    corr = TwoDCorrelation(df)
    sync = corr.sync()
    assert np.allclose(sync.values, np.eye(5) / 4)

def test_async_basic():
    df = pd.DataFrame(np.eye(5), index=[1,2,3,4,5])
    corr = TwoDCorrelation(df)
    async_ = corr.async_()
    assert async_.shape == (5, 5)
