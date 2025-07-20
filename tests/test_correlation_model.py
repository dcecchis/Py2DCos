# tests/test_correlation_model.py
# -*- coding: utf-8 -*-
"""
Tests for CorrelationModel in py2dcos.core.math.correlation_model.py:
- shape mismatch raises
- preprocessing flags invoke PCAProcessor, gaussian and node filters
- baseline subtraction logic for each RefSpectra value
- integration with TwoDCorrelation: correct inputs and outputs
"""
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from py2dcos.config.resources import RefSpectra, CalcMethod
from py2dcos.core.math.correlation_model import CorrelationModel

# A simple 2×3 DataFrame for testing
@pytest.fixture
def df23():
    # columns are 0,1,2 to match numeric indexing in INITIAL/FINAL logic
    return pd.DataFrame([[1, 2, 3], [4, 5, 6]], index=["r1", "r2"], columns=[0, 1, 2])

def test_shape_mismatch_raises(df23):
    other = pd.DataFrame([[1,2,3]], index=["r"], columns=[0,1,2])
    with pytest.raises(ValueError):
        CorrelationModel(df23, other, ref=RefSpectra.ZERO)

def test_preprocessing_and_filters_called(monkeypatch, df23):
    calls = {"pca": 0, "gauss": 0, "node": 0}
    # Stub PCAProcessor.apply
    class DummyPCA:
        def apply(self, spec, n_components, report_filename):
            calls["pca"] += 1
            return spec + 10
    monkeypatch.setattr(
        "py2dcos.core.math.correlation_model.PCAProcessor",
        lambda: DummyPCA()
    )
    # Stub gaussian filter
    def fake_gauss(spec, sigma):
        calls["gauss"] += 1
        return spec + 20
    monkeypatch.setattr(
        "py2dcos.core.math.correlation_model.apply_gaussian_filter",
        fake_gauss
    )
    # Stub node attenuation
    def fake_node(spec):
        calls["node"] += 1
        return spec + 30
    monkeypatch.setattr(
        "py2dcos.core.math.correlation_model.apply_node_attenuation",
        fake_node
    )
    # Stub TwoDCorrelation to avoid heavy math
    import pandas as _pd
    class DummyCore:
        def __init__(self, s1, s2):
            self.input1 = s1.copy()
            self.input2 = s2.copy()
        def sync(self, method):
            return _pd.DataFrame([[42]], index=["x"], columns=["y"])
        def async_(self, method):
            return _pd.DataFrame([[43]], index=["x"], columns=["y"])
    monkeypatch.setattr(
        "py2dcos.core.math.correlation_model.TwoDCorrelation",
        DummyCore
    )

    # instantiate with all preprocess steps active
    model = CorrelationModel(
        df23, df23,
        ref=RefSpectra.ZERO,
        method=CalcMethod.HT,
        reconstruction_comps=1,
        sigma_gaussian=1.5,
        node_attenuation=True
    )

    # PCA.apply should be called twice (spec1 & spec2)
    assert calls["pca"] == 2
    # gaussian filter twice
    assert calls["gauss"] == 2
    # node attenuation twice
    assert calls["node"] == 2

    # DummyCore should have received spec +10+20+30 for both
    expected = df23 + 10 + 20 + 30
    assert_frame_equal(model.core.input1, expected)
    assert_frame_equal(model.core.input2, expected)
    # syncr and asyncr should come from our DummyCore
    assert_frame_equal(model.syncr, pd.DataFrame([[42]], index=["x"], columns=["y"]))
    assert_frame_equal(model.asyncr, pd.DataFrame([[43]], index=["x"], columns=["y"]))

def baseline_expected(df, ref):
    """Compute baseline manually for comparison."""
    desc = df.T.describe().T
    if ref is RefSpectra.ZERO:
        return df
    if ref is RefSpectra.MEAN:
        return df.sub(desc["mean"], axis=0)
    if ref is RefSpectra.MIN:
        return df.sub(desc["min"], axis=0)
    if ref is RefSpectra.MAX:
        return df.sub(desc["max"], axis=0)
    if ref is RefSpectra.INITIAL:
        return df.sub(df[1], axis=0)
    if ref is RefSpectra.FINAL:
        return df.sub(df.iloc[:, -1], axis=0)
    pytest.skip("Unhandled RefSpectra")

@pytest.mark.parametrize("ref", list(RefSpectra))
def test_baseline_subtraction_per_ref(monkeypatch, df23, ref):
    # stub out all preprocess and core to focus on baseline logic
    monkeypatch.setattr(
        "py2dcos.core.math.correlation_model.PCAProcessor",
        lambda: (_ for _ in ()).throw(AssertionError("PCA should not be called"))
    )
    monkeypatch.setattr(
        "py2dcos.core.math.correlation_model.apply_gaussian_filter",
        lambda spec, sigma: (_ for _ in ()).throw(AssertionError("Gaussian should not be called"))
    )
    monkeypatch.setattr(
        "py2dcos.core.math.correlation_model.apply_node_attenuation",
        lambda spec: (_ for _ in ()).throw(AssertionError("NodeAtt should not be called"))
    )
    captured = {}
    class DummyCore2:
        def __init__(self, s1, s2):
            captured["s1"] = s1.copy()
            captured["s2"] = s2.copy()
        def sync(self, method):
            return pd.DataFrame([[0]])
        def async_(self, method):
            return pd.DataFrame([[0]])
    monkeypatch.setattr(
        "py2dcos.core.math.correlation_model.TwoDCorrelation",
        DummyCore2
    )

    model = CorrelationModel(df23, df23, ref=ref)
    exp = baseline_expected(df23, ref)
    assert_frame_equal(captured["s1"], exp)
    assert_frame_equal(captured["s2"], exp)

def test_first_and_last_attrs(df23, monkeypatch):
    # stub core
    class DummyCore3:
        def __init__(self, s1, s2): pass
        def sync(self, method): return pd.DataFrame([[0]])
        def async_(self, method): return pd.DataFrame([[0]])
    monkeypatch.setattr(
        "py2dcos.core.math.correlation_model.TwoDCorrelation",
        DummyCore3
    )
    model = CorrelationModel(df23, df23, ref=RefSpectra.ZERO)
    pd.testing.assert_series_equal(model.first1, df23[1])
    pd.testing.assert_series_equal(model.last1, df23.iloc[:, -1])
    pd.testing.assert_series_equal(model.first2, df23[1])
    pd.testing.assert_series_equal(model.last2, df23.iloc[:, -1])
