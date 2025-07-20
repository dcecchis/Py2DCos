# tests/test_pca_preprocessing.py
# -*- coding: utf-8 -*-
"""
Tests for PCAProcessor.apply in py2dcos.core.math.pca_preprocessing.py:
- n_components <= 0 returns a copy without side effects
- n_components = 1 writes report and correlogram but skips scores plot
- n_components >= 2 writes report, correlogram, and scores plot
"""
import builtins
import io
import pandas as pd
import numpy as np
import pytest
import matplotlib.pyplot as plt
from py2dcos.core.math.pca_preprocessing import PCAProcessor

@pytest.fixture
def df4x3():
    # simple 4×3 DataFrame
    return pd.DataFrame(
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9],
         [10, 11, 12]],
        index=[0, 1, 2, 3],
        columns=['a', 'b', 'c']
    )

class DummyFile(io.StringIO):
    """StringIO that ignores close, so getvalue is available after context exit."""
    def close(self):
        # override to prevent closure
        pass

def test_zero_components_returns_copy_and_no_io(monkeypatch, df4x3):
    p = PCAProcessor()
    # spy open and savefig
    open_calls = []
    def fake_open(fname, mode):
        open_calls.append((fname, mode))
        return DummyFile()
    monkeypatch.setattr(builtins, 'open', fake_open)
    save_calls = []
    monkeypatch.setattr(plt, 'savefig', lambda fname: save_calls.append(fname))

    out = p.apply(
        df4x3,
        n_components=0,
        report_filename='unused.txt',
        plot_correlogram=True,
        correlogram_filename='unused_corr.png',
        plot_scores=True,
        scores_filename='unused_scores.png'
    )
    # Should return equal DataFrame but not same object
    pd.testing.assert_frame_equal(out, df4x3)
    assert out is not df4x3
    # No file I/O should occur when skipping PCA
    assert open_calls == []
    assert save_calls == []

def test_one_component_writes_report_and_correlogram_only(monkeypatch, df4x3):
    p = PCAProcessor()
    # prepare a smaller DF
    df = df4x3.iloc[:3]  # 3×3 subset
    # stub open to use DummyFile
    open_args = []
    report_buf = DummyFile()
    def fake_open(fname, mode):
        open_args.append((fname, mode))
        return report_buf
    monkeypatch.setattr(builtins, 'open', fake_open)
    # stub savefig
    save_args = []
    monkeypatch.setattr(plt, 'savefig', lambda fname: save_args.append(fname))

    out = p.apply(
        df,
        n_components=1,
        report_filename='report1.txt',
        plot_correlogram=True,
        correlogram_filename='corr1.png',
        plot_scores=True,
        scores_filename='scores1.png'
    )
    # output shape and dtype
    assert out.shape == df.shape
    assert out.values.dtype == float
    # reconstructed data is centered (mean approximately 0)
    assert abs(out.values.mean()) < 1e-6

    # Report file opened exactly once for writing
    assert open_args == [('report1.txt', 'w')]
    # Report content starts with PCA Report header
    report_content = report_buf.getvalue()
    assert report_content.startswith("PCA Report")

    # savefig called once for correlogram only
    assert save_args == ['corr1.png']

def test_two_components_writes_all_outputs(monkeypatch, df4x3):
    p = PCAProcessor()
    # stub open to use DummyFile
    open_calls = []
    def fake_open(fname, mode):
        open_calls.append((fname, mode))
        return DummyFile()
    monkeypatch.setattr(builtins, 'open', fake_open)
    # stub savefig
    save_calls = []
    monkeypatch.setattr(plt, 'savefig', lambda fname: save_calls.append(fname))

    out = p.apply(
        df4x3,
        n_components=2,
        report_filename='report2.txt',
        plot_correlogram=True,
        correlogram_filename='corr2.png',
        plot_scores=True,
        scores_filename='scores2.png'
    )
    # output preserves shape
    assert out.shape == df4x3.shape

    # Report file opened once
    assert open_calls == [('report2.txt', 'w')]
    # savefig called for correlogram then scores
    assert save_calls == ['corr2.png', 'scores2.png']
