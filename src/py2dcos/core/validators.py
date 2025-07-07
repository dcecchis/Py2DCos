# src/core/validators.py

import re


def validate_extension(ext1, ext2):
    """
    Validates that the provided file extensions are among the supported types.

    Parameters:
        ext1 (str): The extension of the first file.
        ext2 (str): The extension of the second file (may be an empty string).

    Returns:
        bool: True if both extensions are supported; False otherwise.
    """
    allowed = ["txt", "csv", "xlsx"]
    if ext1 not in allowed:
        return False
    if ext2 and ext2 not in allowed:
        return False
    return True


def validate_method(method):
    """
    Validates that the provided calculation method is supported.

    Parameters:
        method (str): The calculation method (e.g., "HT" or "FFT").

    Returns:
        bool: True if the method is supported; False otherwise.
    """
    allowed_methods = ["HT", "FFT"]
    return method in allowed_methods


def validate_special_case(col_text, row_text):
    """
    Validates special case input for column range and starting row.

    Parameters:
        col_text (str): Expected in the format "A:B" (or similar with 1-3 letters).
        row_text (str): A string that should represent a numeric row value.

    Returns:
        bool: True if the input is valid; False otherwise.
    """
    # Validate column text with a regex
    if not re.match(r"^[a-zA-Z]{1,3}:[a-zA-Z]{1,3}$", col_text):
        return False
    if not row_text.isdigit():
        return False
    return True