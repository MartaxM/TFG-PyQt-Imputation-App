import pandas as pd
import numpy as np
import math

def removePercentage(df, percent = 0.5):
    max = len(df.index)
    n = percent * max
    n = int( math.floor(n))
    indexes = np.random.permutation(max)[:n].tolist()
    dropped = df.drop(df.index[indexes])
    return dropped

def removeInterval(df, start, end, datetimeCol = 'time'):
    df = df.copy()
    df[datetimeCol] = pd.to_datetime(df[datetimeCol])
    df[datetimeCol] = df[datetimeCol].dt.floor('S')  # Round down to seconds
    dropped = df[(df[datetimeCol] < start) | (df[datetimeCol] > end)]

    return dropped

def removeOutsideInterval(df, start, end, datetimeCol = 'time'):
    df = df.copy()
    df[datetimeCol] = pd.to_datetime(df[datetimeCol])
    dropped = df[(df[datetimeCol] >= start) & (df[datetimeCol] <= end)].copy()
    return dropped

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