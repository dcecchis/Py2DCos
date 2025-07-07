from PyQt5.QtWidgets import QMessageBox
import re


def ValidateMethod(method):
    """
    ValidateMethod function.
    Validates if the given method is supported by the application.
    """
    if method == "FFT":
        msg = QMessageBox()
        msg.setText("Ups, FFT not yet developed")
        x = msg.exec_()
        return False

    if method == "HT":
        return True


def ValidateExtension(extension1, extension2):
    """
    ValidateExtension function.
    Checks if the provided file extensions are supported.
    """
    available = ["txt", "csv", "xlsx"]

    if extension1 in available:
        T1 = True
    else:
        msg = QMessageBox()
        msg.setText("Ups, we can't handle " + extension1 + " files")
        x = msg.exec_()
        return False
    if extension2 in available or extension2 == '':
        T2 = True
    else:
        msg = QMessageBox()
        msg.setText("Ups, we can't handle " + extension2 + " files")
        x = msg.exec_()
        return False
    if T1 and T2:
        return True


def ValidateSpecialCase(columntxt, rowtxt):
    """
    ValidateSpecialCase function.
    Validates the special case input for columns and rows.
    """

    x = re.search("^[a-z,A-Z]{1,3}:[a-z,A-Z]{1,3}$", columntxt)

    if x and rowtxt.isnumeric():
        return True
    else:
        msg = QMessageBox()
        msg.setText("Invalid input")
        x = msg.exec_()
        return False
