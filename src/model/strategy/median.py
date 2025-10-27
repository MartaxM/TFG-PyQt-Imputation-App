from model.strategy.imputation import Imputation
import numpy as np
import pandas as pd

class Median(Imputation):

    def impute(self, df, column):
        # Reindexear es una cosa que deberiamos hacer fuera de aquí
        # Creamos array de valores correctos
        valid = df.copy()
        valid = valid.dropna(subset = [column])
        valid= valid.reset_index()
        # Reindexear para completar valores faltantes
        validLength = len(valid)
        result = df.copy()

        median = valid[column].median()
        result[column] = result[column].fillna(value=median)
        
        return result
    
    @property
    def label(self):
        return('Median')

        