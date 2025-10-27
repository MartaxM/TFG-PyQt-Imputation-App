from model.strategy.imputation import Imputation
import numpy as np

class BackwardFill(Imputation):

    def impute(self, df, column):
        # Reindexear es una cosa que deberiamos hacer fuera de aquí
        # Creamos array de valores correctos
        valid = df.copy()
        valid = valid.dropna(subset = [column])
        valid= valid.reset_index()
        validLength = len(valid)
        result = df.copy()
        # Ponemos preValid y nextValid con el valor de las rows 0 y 1 de los valores válidos
        nextValidInx = 0
        nextValid = valid.loc[nextValidInx]
        index = 0
        # Mientras que el siguiente valor válido que necesitamos no se salga de los existentes
        while(nextValidInx < validLength):
            nextValid = valid.loc[nextValidInx]
            # Si el valor de la fila en la columna indicada es NaN se llena con el siguiente valor
            if np.isnan(result.at[index, column]):
                result.at[index, column] = nextValid[column]
                result.at[index, 'imputated'] = True
            # Si no, se entiende que es un valor válido, por tanto movemos el indice del siguiente valor que se usa para rellenar
            else:
                nextValidInx += 1

            index += 1
        
        return result
    
    @property
    def label(self):
        return 'BackwardFill'

        