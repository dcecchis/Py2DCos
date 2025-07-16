import pandas as pd
import numpy as np

def reader(filename):
    """
    Accepts
      [path, "csv"]
      [path, "txt"]
      [path, "xlsx", sheet, row, col, labeled]   # new
    and returns a DataFrame.
    """
    # handle csv files by reading without headers and using first column as index
    if filename[1] == "csv":
        return pd.read_csv(filename[0], header=None, index_col=0)

    # handle text files similarly but with space delimiter
    if filename[1] == "txt":
        return pd.read_csv(filename[0], header=None, index_col=0, sep=" ")

    # handle excel files, accommodating both legacy and new parameter formats
    if filename[1] == "xlsx":
        # inspect last tuple element to decide if labeled flag is included
        if isinstance(filename[-1], bool):
            # new style: unpack sheet, row, column, and labeled flag
            sheet, row, column, labeled = filename[-4:]
        else:
            # legacy style: unpack only sheet, row, and column
            sheet, row, column = filename[-3:]
            labeled = False

        # convert starting row to integer if provided; default to first row when blank
        try:
            row_i = int(row) if str(row).strip() else 1
        except ValueError as exc:
            # enforce that row must be a valid integer
            raise ValueError(
                f"Starting Row must be an integer, got '{row}'."
            ) from exc

        # compute number of rows to skip so data begins at the correct line
        skip_rows = row_i - 1

        # read the specified sheet, columns, and rows from excel into a DataFrame
        spec1 = pd.read_excel(
            filename[0],
            header=None,
            index_col=0,
            sheet_name=sheet,
            usecols=column,
            skiprows=skip_rows,
        )

        # if labeled interpolation requested, fetch labels and apply interpolation
        if labeled:
            # derive next column letter to capture header labels
            first_col = column.split(":")[0]
            next_col  = chr(ord(first_col) + 1)
            label_range = next_col + column[1:]

            # read a single header row of labels for interpolation reference
            labels = pd.read_excel(
                filename[0],
                header=None,
                sheet_name=sheet,
                usecols=label_range,
                skiprows=skip_rows - 1,
                nrows=1,
            ).values[0]

            # only interpolate when labels are numeric and unevenly spaced
            if checklabels(labels):
                spec1 = interp(spec1, labels)

        return spec1

# public helper – build the tuple that `reader()` expects
def resolve_file(
    base: tuple[str, str] | None,
    excel_params: tuple | None = None,
) -> tuple | None:
    """
    Return a filename-spec compatible with ``reader()``
    """
    if base is None:
        return None
    path, ext = base
    if ext == "xlsx" and excel_params:
        return (path, ext, *excel_params)
    return base


def checkHeader(df):
    # ensure column headers form a simple numeric sequence if they aren’t already
    col = df.columns
    # check whether first+last header equals expected sum for uniform numeric sequence
    if float(col[0]) + float(col[-1]) != len(col) + 1:
        head = np.linspace(1, len(col), len(col))
        df.columns = head
    return df

def checklabels(labelRow):
    # only consider interpolation when label row contains numeric values
    if all(isinstance(element, (int, float)) for element in labelRow):
        # compute differences between consecutive labels
        differences = [labelRow[i + 1] - labelRow[i] for i in range(len(labelRow) - 1)]
        # return true when spacing varies, indicating need for interpolation
        return not all(differences[0] == diff for diff in differences)
    # skip interpolation when labels are non-numeric
    return False

def interp(df, spacing):
    # set dataframe column labels to the provided spacing list for reference
    new_spacing = np.linspace(spacing[0], spacing[-1], len(spacing))
    df.columns = spacing

    # add any missing columns as nan so interpolation can fill gaps
    for column in new_spacing:
        if column not in df.columns:
            df[column] = np.nan

    # sort columns to match numeric order before interpolation
    df = df.sort_index(axis=1)
    # interpolate across columns to create uniform spacing
    df = df.interpolate(axis=1, method='index')

    # remove extra columns not in the target spacing to clean up result
    for column in df.columns:
        if column not in new_spacing:
            df = df.drop(column, axis=1)

    return df
