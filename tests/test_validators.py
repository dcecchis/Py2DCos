# tests/test_validators.py
# -*- coding: utf-8 -*-
import pytest
from py2dcos.core.validators import (
    validate_method,
    validate_extension,
    validate_special_case,
    UnsupportedMethodError,
    UnsupportedExtensionError,
    InvalidExcelFormatError,
)
from py2dcos.config.resources import CalcMethod

def test_validate_method_ht():
    # HT is supported
    assert validate_method(CalcMethod.HT) is None

def test_validate_method_non_ht_raises():
    # any other method raises
    with pytest.raises(UnsupportedMethodError) as exc:
        validate_method(CalcMethod.FFT)
    assert "not yet supported" in str(exc.value)

@pytest.mark.parametrize("ext1,ext2", [
    ("txt", ""),
    ("csv", None),
    ("xlsx", "txt"),
    ("csv", "xlsx"),
])
def test_validate_extension_valid(ext1, ext2):
    # valid primary and (optional) secondary extensions do not raise
    if ext2 is None:
        validate_extension(ext1)
    else:
        validate_extension(ext1, ext2)

@pytest.mark.parametrize("invalid_ext", ["pdf", "doc", "exe"])
def test_validate_extension_invalid_primary(invalid_ext):
    with pytest.raises(UnsupportedExtensionError) as exc:
        validate_extension(invalid_ext)
    assert f"we can't handle '{invalid_ext}' files" in str(exc.value)

def test_validate_extension_invalid_secondary():
    with pytest.raises(UnsupportedExtensionError) as exc:
        validate_extension("csv", "pdf")
    assert "we can't handle 'pdf' files" in str(exc.value)

@pytest.mark.parametrize("col,row", [
    ("A:C", "1"),
    ("AA:ZZ", "123"),
    ("abc:DEF", "999"),
    ("x:Y", "0"),
])
def test_validate_special_case_valid(col, row):
    # valid column range and numeric row
    assert validate_special_case(col, row) is None

@pytest.mark.parametrize("col,row", [
    ("A-:C", "10"),   # invalid column format
    ("1:A", "5"),     # column contains digit
    ("AB:CD:E", "7"), # too many parts
    ("A:C", "1.0"),   # non-integer row
    ("A:C", "ten"),   # non-numeric row
    ("A C", "10"),    # space instead of colon
])
def test_validate_special_case_invalid(col, row):
    with pytest.raises(InvalidExcelFormatError):
        validate_special_case(col, row)
