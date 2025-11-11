import pandas as pd
import numpy as np
import math

def removePercentage(df, percent = 0.5):
    removed = df.copy()
    max = len(df.index)
    n = percent * max
    n = int( math.floor(n))
    indexes = np.random.permutation(max)[:n].tolist()
    removed.loc[df.index[indexes]] = np.nan
    return removed

def removeInterval(df, start, end, datetimeCol = 'time'):
    removed = df.copy()
    removed[datetimeCol] = pd.to_datetime(removed[datetimeCol])
    removed[datetimeCol] = removed[datetimeCol].dt.floor('S')  # Round down to seconds
    mask = (removed[datetimeCol] >= start) & (removed[datetimeCol] <= end)
    mask.loc[mask] = np.nan

    return removed

def removeOutsideInterval(df, start, end, datetimeCol = 'time'):
    removed = df.copy()
    removed[datetimeCol] = pd.to_datetime(removed[datetimeCol])
    mask = (removed[datetimeCol] < start) | (removed[datetimeCol] > end)
    removed.loc[mask] = np.nan
    return removed

# Version que ponen NaN en vez de eliminar
# def removePercentage(df, percent = 0.5):
#     max = len(df.index)
#     n = percent * max
#     n = int( math.floor(n))
#     # indexes = random.permutation(max)[:n].tolist()
#     # dropped = df.drop(df.index[indexes])
#     indexes = np.random.permutation(max)[:n]
#     dropped = df.copy()
#     dropped.loc[indexes] = np.nan
#     print(dropped)
#     # return dropped.reset_index(drop=True)
#     return dropped