import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from py2dcos.core.io.loader import check_header, DataLoader
from py2dcos.core.validators import UnsupportedExtensionError
from py2dcos.types import InputFile

# --- Tests for check_header ---

def test_check_header_no_change():
    # columns form 1-based numeric sequence: 1,2,3
    df = pd.DataFrame([[1, 2, 3]], columns=[1.0, 2.0, 3.0])
    out = check_header(df.copy())
    pd.testing.assert_frame_equal(out, df)


def test_check_header_relabels():
    # columns [1,5,9] should relabel to [1,2,3]
    df = pd.DataFrame([[10, 20, 30]], index=[0], columns=[1.0, 5.0, 9.0])
    out = check_header(df.copy())
    assert list(out.columns) == list(np.linspace(1, 3, 3))

# --- Tests for DataLoader.load ---

@ pytest.fixture(autouse=True)
def stub_validate(monkeypatch):
    # avoid validate_extension side-effects except in specific tests
    monkeypatch.setattr(
        'py2dcos.core.io.loader.validate_extension',
        lambda ext: None
    )

class DummyDF(pd.DataFrame):
    pass

@ pytest.mark.parametrize("ext,sep_arg", [
    ("csv", None),
    ("txt", ' '),
])
def test_load_csv_and_txt(monkeypatch, tmp_path, ext, sep_arg):
    # prepare fake DataFrame with non-sequential columns to test check_header
    fake_df = pd.DataFrame([[1, 2, 3], [4, 5, 6]], index=[0,1], columns=[1.0, 3.0, 5.0])
    calls = {}
    def fake_read_csv(path, header, index_col, sep=None):
        calls['path'] = path
        calls['header'] = header
        calls['index_col'] = index_col
        calls['sep'] = sep
        return fake_df.copy()
    # patch pandas.read_csv inside loader
    monkeypatch.setattr(
        'py2dcos.core.io.loader.pd.read_csv',
        fake_read_csv
    )
    # instantiate InputFile
    file = InputFile(path=str(tmp_path / f"file.{ext}"), extension=ext, excel_params=None)
    out = DataLoader.load(file)
    # validate read_csv args
    assert isinstance(calls['path'], Path)
    assert str(calls['path']) == str(tmp_path / f"file.{ext}")
    assert calls['header'] is None
    assert calls['index_col'] == 0
    assert calls['sep'] == sep_arg
    # check_header should relabel columns to [1,2,3]
    assert list(out.columns) == list(np.linspace(1, 3, 3))


def test_load_unsupported_extension():
    # do not stub validate_extension to test raising
    file = InputFile(path='x.xyz', extension='xyz', excel_params=None)
    with pytest.raises(UnsupportedExtensionError):
        DataLoader.load(file)


def test_load_xlsx_missing_params():
    # xlsx without excel_params should error
    file = InputFile(path='x.xlsx', extension='xlsx', excel_params=None)
    with pytest.raises(UnsupportedExtensionError) as exc:
        DataLoader.load(file)
    assert 'requires sheet / row / column' in str(exc.value)


def test_load_xlsx_with_params(monkeypatch, tmp_path):
    # prepare fake DataFrame to be returned by read_excel
    fake_df = pd.DataFrame([[7, 8], [9, 10]], index=[0,1], columns=[1.0, 4.0])
    # stub read_excel in loader
    monkeypatch.setattr(
        'py2dcos.core.io.loader.read_excel',
        lambda path, sheet, row, cols, labelled: fake_df.copy()
    )
    # stub validate_extension
    # prepare InputFile with excel_params
    params = ('Sheet1', '2', 'A:B', False)
    file = InputFile(path=str(tmp_path / 'f.xlsx'), extension='xlsx', excel_params=params)
    out = DataLoader.load(file)
    # check that fake_df was returned and check_header applied: relabel columns [1,4] -> [1,2]
    assert list(out.columns) == list(np.linspace(1, 2, 2))
