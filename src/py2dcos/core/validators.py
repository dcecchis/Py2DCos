import re

# define error when user requests a correlation method that isn’t implemented yet
class UnsupportedMethodError(ValueError):
    pass

# define error when input file extension isn’t one of the allowed types
class UnsupportedExtensionError(ValueError):
    pass

# define error for invalid excel parameter inputs (column range or starting row)
class InvalidExcelFormatError(ValueError):
    pass

def validate_method(method):
    # only hilbert transform is supported at this time
    if method == "HT":
        return
    # inform user that other methods are planned but not yet available
    raise UnsupportedMethodError(f"the method '{method}' is not yet supported.")

def validate_extension(extension1, extension2=""):
    # limit file types to plain text, csv, or excel for predictable parsing
    available = {"txt", "csv", "xlsx"}
    if extension1 not in available:
        # catch unsupported primary extension early
        raise UnsupportedExtensionError(f"we can't handle '{extension1}' files.")
    if extension2 and extension2 not in available:
        # catch unsupported secondary extension early
        raise UnsupportedExtensionError(f"we can't handle '{extension2}' files.")

def validate_special_case(columntxt, rowtxt):
    # require column range in form letters:letters (e.g. A:C) and numeric row for consistency
    pattern = r"^[a-zA-Z]{1,3}:[a-zA-Z]{1,3}$"
    if re.match(pattern, columntxt) and rowtxt.isnumeric():
        return
    # prompt user to correct format so downstream parsing is reliable
    raise InvalidExcelFormatError("invalid input for column/row specification.")
