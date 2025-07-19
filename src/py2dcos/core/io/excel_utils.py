import numpy as np
import pandas as pd
from py2dcos.core.validators import validate_special_case

def read_excel(path, sheet, row, col_range, labelled) -> pd.DataFrame:
    validate_special_case(col_range, row)
    row_i = int(row) if str(row).strip() else 1
    skip_rows = row_i - 1

    df = pd.read_excel(
        path, header=None, index_col=0, sheet_name=sheet,
        usecols=col_range, skiprows=skip_rows
    )

    if labelled:
        first_col = col_range.split(":")[0]
        next_col  = chr(ord(first_col) + 1)
        label_rng = next_col + col_range[1:]

        labels = pd.read_excel(
            path, header=None, sheet_name=sheet, usecols=label_rng,
            skiprows=skip_rows - 1, nrows=1
        ).values[0]

        if _check_labels(labels):
            df = _interp(df, labels)

    return df

def _check_labels(row):
    if all(isinstance(x, (int, float)) for x in row):
        diffs = np.diff(row)
        return not np.allclose(diffs, diffs[0])
    return False

def _interp(df, spacing):
    new_spacing = np.linspace(spacing[0], spacing[-1], len(spacing))
    df.columns = spacing
    for col in new_spacing:
        if col not in df.columns:
            df[col] = np.nan
    df = df.sort_index(axis=1).interpolate(axis=1, method="index")
    df = df[[c for c in df.columns if c in new_spacing]]
    return df
