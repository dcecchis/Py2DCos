# tests/test_excel_utils.py
# -*- coding: utf-8 -*-
"""
Tests for read_excel, _check_labels, and _interp in py2dcos.core.io.excel_utils.py
"""
import numpy as np
import pandas as pd
import pytest

import py2dcos.core.io.excel_utils as eu

def test_check_labels():
    # all numeric but uniform diffs -> False
    row = np.array([0.0, 5.0, 10.0])
    assert eu._check_labels(row) is False
    # numeric with non-uniform diffs -> True
    row2 = np.array([0.0, 5.0, 12.0])
    assert eu._check_labels(row2) is True
    # non-numeric entry -> False
    row3 = np.array([0.0, "x", 2.0], dtype=object)
    assert eu._check_labels(row3) is False

def test_interp_homogeneous_and_interpolation():
    # DataFrame with two rows, three initial columns
    df = pd.DataFrame([[10,20,30],[40,50,60]],
                      index=[0,1],
                      columns=[0.0,1.0,2.0])
    # spacing with non-uniform diffs => [0,5,12]
    spacing = np.array([0.0, 5.0, 12.0])
    out = eu._interp(df.copy(), spacing)
    # new columns == linspace(0,12,3) = [0.0,6.0,12.0]
    expected_cols = list(np.linspace(0.0, 12.0, 3))
    assert np.allclose(out.columns.astype(float), expected_cols)
    # ensure interpolation at 6.0 between 20 and 30 for row0
    val06 = out.loc[0.0, 6.0]
    assert pytest.approx(20.0 + (30.0-20.0)*(6.0-5.0)/(12.0-5.0), rel=1e-3) == val06

@pytest.fixture(autouse=True)
def stub_validate(monkeypatch):
    # skip format validation
    monkeypatch.setattr(eu, "validate_special_case", lambda c, r: None)

def make_fake_read(df_main, labels_row):
    """
    Returns a fake pd.read_excel that:
     - when called without nrows or nrows != 1 returns df_main
     - when called with nrows==1 returns a DataFrame whose row is labels_row
    """
    def fake_read(*args, **kwargs):
        nrows = kwargs.get("nrows", None)
        usecols = kwargs.get("usecols")
        if nrows == 1:
            # return labels as a one-row DataFrame
            return pd.DataFrame([labels_row], columns=[*df_main.columns])
        # otherwise return main df
        return df_main.copy()
    return fake_read

def test_read_excel_without_label(monkeypatch):
    # setup df_main
    df_main = pd.DataFrame([[100,200],[300,400]], index=[0,1], columns=[0,1])
    fake = make_fake_read(df_main, labels_row=[0,1])
    monkeypatch.setattr(eu.pd, "read_excel", fake)
    # labelled=False should skip label logic
    out = eu.read_excel("fake.xlsx", sheet="S", row="1", col_range="A:B", labelled=False)
    pd.testing.assert_frame_equal(out, df_main)

def test_read_excel_labelled_uniform_labels(monkeypatch):
    # uniform labels -> no interp, df unchanged
    df_main = pd.DataFrame([[1,2,3],[4,5,6]], index=[0,1], columns=[0,1,2])
    fake = make_fake_read(df_main, labels_row=[0.0,5.0,10.0])
    monkeypatch.setattr(eu.pd, "read_excel", fake)
    out = eu.read_excel("fake.xlsx", sheet="S", row="2", col_range="A:C", labelled=True)
    pd.testing.assert_frame_equal(out, df_main)

def test_read_excel_labelled_nonuniform_triggers_interp(monkeypatch):
    # non-uniform labels -> interp applied
    df_main = pd.DataFrame([[10,20,30],[40,50,60]], index=[0,1], columns=[0,1,2])
    labels = [0.0, 5.0, 12.0]
    fake = make_fake_read(df_main, labels_row=labels)
    monkeypatch.setattr(eu.pd, "read_excel", fake)
    out = eu.read_excel("fake.xlsx", sheet="S", row="3", col_range="A:C", labelled=True)
    # columns should be linspace(0,12,3): [0.0,6.0,12.0]
    expected_cols = list(np.linspace(0.0, 12.0, 3))
    assert np.allclose(out.columns.astype(float), expected_cols)
    # original values at column 0 and 12 should match and mid is interpolated
    assert out.loc[0, expected_cols[0]] == 10
    assert out.loc[0, expected_cols[2]] == 30
    mid = expected_cols[1]
    # interpolation check for row0
    expected_mid = 20 + (30-20)*(mid-5.0)/(12.0-5.0)
    assert pytest.approx(expected_mid, rel=1e-3) == out.loc[0, mid]
