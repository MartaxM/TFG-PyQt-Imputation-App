from model.strategy.imputation import Imputation
import numpy as np

class ForwardFill(Imputation):

    def impute(self, df, column, args = None):
        # Creamos array de valores correctos
        valid = df.copy()
        valid = valid.dropna(subset = [column])
        valid= valid.reset_index()
        validLength = len(valid)
        result = df.copy()
        # Ponemos preValid y nextValid con el valor de las rows 0 y 1 de los valores válidos
        preValid = valid.loc[0]
        nextValidInx = 1
        
        index = valid.at[0, 'index'] + 1
        # Mientras que el siguiente valor válido que necesitamos no se salga de los existentes
        while(nextValidInx < validLength):
            # Si el valor de la fila en la columna indicada es NaN se rellena con el anterior valor válido más cercano
            if np.isnan(result.at[index, column]):
                result.at[index, column] = preValid[column]
            # Si no, se entiende que es un valor válido, por tanto actualizamos los índices de valores válidos
            else:
                preValid = valid.loc[nextValidInx]
                nextValidInx += 1
            index += 1
        
        return result
    
    @property
    def label(self):
        return 'ForwardFill'

        