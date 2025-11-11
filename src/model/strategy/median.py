from model.strategy.imputation import Imputation
import numpy as np
import pandas as pd

class Median(Imputation):

    def impute(self, df, column, args = None):
        # Creamos array de valores correctos
        valid = df.copy()
        valid = valid.dropna(subset = [column])
        valid = valid.reset_index()
        
        window = None
        validLength = len(valid)
        result = df.copy()
        if validLength < 4:
            window = valid
        else:
            window = valid.head(4)

        median = window[column].median()
        nextValidInx = 4

        for index, row in df.iterrows():
            if np.isnan(result.at[index, column]):
                result.at[index, column] = median
            else:
                window = window.drop(window.index[0])
                if nextValidInx < len(df):
                    window = pd.concat([window, df.loc[[nextValidInx]]], ignore_index=True)
                    nextValidInx += 1

        return result
    
    @property
    def label(self):
        return('Median')

        