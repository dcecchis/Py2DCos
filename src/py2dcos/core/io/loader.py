from pathlib import Path
import pandas as pd
import numpy as np

from py2dcos.datatypes import InputFile
from py2dcos.core.validators import (
    validate_extension, UnsupportedExtensionError
)
from .excel_utils import read_excel

def check_header(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure the DataFrame columns form a 1-based numeric sequence.
    """
    col = df.columns
    if float(col[0]) + float(col[-1]) != len(col) + 1:
        df.columns = np.linspace(1, len(col), len(col))
    return df


class DataLoader:
    """
    Read any supported InputFile into a clean Pandas DataFrame.
    """

    @staticmethod
    def load(file: InputFile) -> pd.DataFrame:
        validate_extension(file.extension)

        ext = file.extension.lower()
        path = Path(file.path)

        if ext == "csv":
            df = pd.read_csv(path, header=None, index_col=0)

        elif ext == "txt":
            df = pd.read_csv(path, header=None, index_col=0, sep=" ")

        elif ext == "xlsx":
            if file.excel_params is None:
                raise UnsupportedExtensionError(
                    "Excel file requires sheet / row / column information."
                )
            sheet, row, cols, labelled = file.excel_params
            df = read_excel(path, sheet, row, cols, labelled)

        else:
            # validate_extension already caught this, but for mypy completeness:
            raise UnsupportedExtensionError(ext)

        return check_header(df)
