import re

# Custom exceptions
class UnsupportedMethodError(ValueError):
    pass

class UnsupportedExtensionError(ValueError):
    pass

class InvalidExcelFormatError(ValueError):
    pass

# FFT not yet implemented
def validate_method(method):
    if method == "HT":
        return
    raise UnsupportedMethodError(f"The method '{method}' is not yet supported.")

# Only allow txt, csv, xlsx
def validate_extension(extension1, extension2=""):
    available = {"txt", "csv", "xlsx"}
    if extension1 not in available:
        raise UnsupportedExtensionError(f"We can't handle '{extension1}' files.")
    if extension2 and extension2 not in available:
        raise UnsupportedExtensionError(f"We can't handle '{extension2}' files.")

# Excel cell range format validation
def validate_special_case(columntxt, rowtxt):
    if re.match(r"^[a-zA-Z]{1,3}:[a-zA-Z]{1,3}$", columntxt) and rowtxt.isnumeric():
        return
    raise InvalidExcelFormatError("Invalid input for column/row specification.")
