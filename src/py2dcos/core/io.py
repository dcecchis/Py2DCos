import pandas as pd
import numpy as np

def reader(filename):
    # load CSV when ext is 'csv'
    if filename[1] == "csv":
        spec1 = pd.read_csv(filename[0], header=None, index_col=0)
        return spec1

    # load Excel when ext is 'xlsx'
    if filename[1] == "xlsx":
        # unpack sheet, row, column from the filename list
        sheet, row, column = filename[-4:-1]
        row = int(row)
        skipRows = row - 1
        # read the data matrix
        spec1 = pd.read_excel(filename[0], header=None, index_col=0, sheet_name=sheet, usecols=column,
                              skiprows=skipRows)

        # if labels are present, read and interpolate
        if filename[-1] == True:
            firstCol = column.split(':')[0]  # first column of the column range
            nextCol = chr(
                ord(firstCol) + 1)  # get the following column, because the heading of the wavenumber column isnt relevant
            colRange = nextCol + column[1:]
            labels = pd.read_excel(filename[0], header=None, sheet_name=sheet, usecols=colRange, skiprows=skipRows - 1,
                                   nrows=1).values[0]
            if checklabels(labels):  # checks if labels are numbers and if they are equally spaced
                spec1 = interp(spec1, labels)
        return spec1

    # load text when ext is 'txt'
    if filename[1] == "txt":
        spec1 = pd.read_csv(filename[0], header=None, index_col=0, sep=" ")
        return spec1


def checkHeader(df):
    # ensure column labels are consecutive numbers starting at 1
    col = df.columns
    if float(col[0]) + float(col[-1]) != len(col) + 1:
        head = np.linspace(1, len(col), len(col))
        df.columns = head
    return df


def checklabels(labelRow): 
    # return True if labelRow is numeric and equally spaced
    if all(isinstance(element, (int, float)) for element in labelRow):  # check if labels are only nums
        differences = [labelRow[i + 1] - labelRow[i] for i in range(len(labelRow) - 1)]
        eqSpaced = not all(differences[0] == diff for diff in differences)  # checks if nums are equally spaced
        return eqSpaced
    return False


def interp(df, spacing):
    # interpolate DataFrame columns to match new spacing
    new_spacing = np.linspace(spacing[0], spacing[-1], len(spacing))
    df.columns = spacing

    # add missing columns as NaN
    for column in new_spacing:
        a = column not in df.columns
        if column not in df.columns:
            df[column] = np.nan

    df = df.sort_index(axis=1)
    df = df.interpolate(axis=1, method='index')

    # drop extra columns beyond new_spacing
    for column in df.columns:
        if column not in new_spacing:
            df = df.drop(column, axis=1)

    return df