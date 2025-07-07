import pandas as pd
import numpy as np

def reader(filename):
    if filename[1] == "csv":
        spec1 = pd.read_csv(filename[0], header=None, index_col=0)
        return spec1

    if filename[1] == "xlsx":
        ## The default option (only the matrix)
        # try:
        sheet, row, column = filename[-4:-1]
        row = int(row)
        skipRows = row - 1
        spec1 = pd.read_excel(filename[0], header=None, index_col=0, sheet_name=sheet, usecols=column,
                              skiprows=skipRows)

        if filename[-1] == True:  # check if columns are labeled
            firstCol = column.split(':')[0]  # first column of the column range
            nextCol = chr(
                ord(firstCol) + 1)  # get the following column, because the heading of the wavenumber column isnt relevant
            colRange = nextCol + column[1:]
            labels = pd.read_excel(filename[0], header=None, sheet_name=sheet, usecols=colRange, skiprows=skipRows - 1,
                                   nrows=1).values[0]
            if checklabels(labels):  # checks if labels are numbers and if they are equally spaced
                spec1 = interp(spec1, labels)
            else:
                pass

        # except:
        # spec1 = pd.read_excel(filename[0], header=None, index_col=0)

        # spec1 = pd.read_excel(filename[0], header=0, index_col=0)
        return spec1

    if filename[1] == "txt":
        spec1 = pd.read_csv(filename[0], header=None, index_col=0, sep=" ")
        return spec1


def checkHeader(df):
    ##### This functon seems not to work properly, I changed the header and
    ##### it looks to work now... But check if it is want you wanted
    col = df.columns
    # if float(col[0]) + float(col[-1]) == len(col)+1:
    #     pass
    # else:
    if float(col[0]) + float(col[-1]) != len(col) + 1:
        head = np.linspace(1, len(col), len(col))
        df.columns = head

    return df


def checklabels(labelRow):  # checks if labels are numbers and if they are equally spaced
    if all(isinstance(element, (int, float)) for element in labelRow):  # check if labels are only nums
        differences = [labelRow[i + 1] - labelRow[i] for i in range(len(labelRow) - 1)]
        eqSpaced = not all(differences[0] == diff for diff in differences)  # checks if nums are equally spaced
        return eqSpaced
    else:
        return False


def interp(df, spacing):
    new_spacing = np.linspace(spacing[0], spacing[-1], len(spacing))
    df.columns = spacing

    for column in new_spacing:
        a = column not in df.columns
        if column not in df.columns:
            df[column] = np.nan

    df = df.sort_index(axis=1)
    df = df.interpolate(axis=1, method='index')

    for column in df.columns:
        if column not in new_spacing:
            df = df.drop(column, axis=1)

    return df