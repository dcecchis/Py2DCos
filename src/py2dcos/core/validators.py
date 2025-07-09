import re

# Custom exceptions for invalid inputs
class UnsupportedMethodError(ValueError):
    pass

class UnsupportedExtensionError(ValueError):
    pass

class InvalidExcelFormatError(ValueError):
    pass

def validate_method(method):
    # only 'HT' (Hilbert Transform) is supported
    if method == "HT":
        return
    raise UnsupportedMethodError(f"The method '{method}' is not yet supported.")

def validate_extension(extension1, extension2=""):
    # allow only txt, csv, xlsx extensions
    available = {"txt", "csv", "xlsx"}
    if extension1 not in available:
        raise UnsupportedExtensionError(f"We can't handle '{extension1}' files.")
    if extension2 and extension2 not in available:
        raise UnsupportedExtensionError(f"We can't handle '{extension2}' files.")

def validate_special_case(columntxt, rowtxt):
    # ensure Excel range like 'A:C' and numeric row
    if re.match(r"^[a-zA-Z]{1,3}:[a-zA-Z]{1,3}$", columntxt) and rowtxt.isnumeric():
        return
    raise InvalidExcelFormatError("Invalid input for column/row specification.")
