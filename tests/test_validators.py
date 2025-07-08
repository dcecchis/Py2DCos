# tests/test_validators.py
import pytest

from py2dcos.core.validators import (
    validate_method,
    validate_extension,
    validate_special_case,
    UnsupportedMethodError,
    UnsupportedExtensionError,
    InvalidExcelFormatError,
)

# ---------- validate_method --------------------------------------------------


def test_validate_method_accepts_ht():
    # Should not raise for the only supported method
    validate_method("HT")


@pytest.mark.parametrize("bad_method", ["FFT", "DWT", "", None])
def test_validate_method_rejects_unsupported(bad_method):
    with pytest.raises(UnsupportedMethodError):
        validate_method(bad_method)


# ---------- validate_extension -----------------------------------------------


@pytest.mark.parametrize(
    "ext1, ext2",
    [
        ("txt", ""),
        ("csv", ""),
        ("xlsx", ""),
        ("txt", "csv"),
        ("csv", "xlsx"),
        ("xlsx", "txt"),
    ],
)
def test_validate_extension_accepts_known(ext1, ext2):
    # Should run without exception for any allowed combination
    validate_extension(ext1, ext2)


@pytest.mark.parametrize(
    "ext1, ext2",
    [
        ("pdf", ""),
        ("", ""),
        ("txt", "pdf"),
        ("json", "csv"),
        ("csv", "xml"),
    ],
)
def test_validate_extension_rejects_unknown(ext1, ext2):
    with pytest.raises(UnsupportedExtensionError):
        validate_extension(ext1, ext2)


# ---------- validate_special_case --------------------------------------------


@pytest.mark.parametrize(
    "column, row",
    [
        ("A:B", "1"),
        ("AA:AB", "10"),
        ("X:Z", "999"),
        ("a:c", "5"),  # lower-case columns allowed
    ],
)
def test_validate_special_case_accepts_well_formed(column, row):
    validate_special_case(column, row)


@pytest.mark.parametrize(
    "column, row",
    [
        ("1:2", "1"),        # invalid column letters
        ("A1:B2", "3"),      # embedded digits
        ("A:B:C", "4"),      # too many parts
        ("A:B", "row"),      # non-numeric row
        ("", "1"),           # empty column
        ("A:B", ""),         # empty row
    ],
)
def test_validate_special_case_rejects_bad_input(column, row):
    with pytest.raises(InvalidExcelFormatError):
        validate_special_case(column, row)
