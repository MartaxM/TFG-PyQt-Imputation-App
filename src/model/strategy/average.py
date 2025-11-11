from model.strategy.imputation import Imputation
import numpy as np

class Average(Imputation):
    
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
        nextValid = valid.loc[nextValidInx]

        # 'index' almacena su valor de indice anterior, hasta alcanzar el valor que corresponde a su indice en la secuencia
        # rellenamos con el valor de preValid
        for i in range(0, valid.at[0, 'index']):
            result.at[i, column] = preValid[column]
        
        index = valid.at[0, 'index'] + 1
        # Mientras que el siguiente valor válido que necesitamos no se salga de los existentes
        while(nextValidInx < validLength):
            nextValid = valid.loc[nextValidInx]
            # Si el valor de la fila en la columna indicada es NaN se hace la media
            if np.isnan(result.at[index, column]):
                result.at[index, column] = (preValid[column] + nextValid[column]) / 2
            # Si no, se entiende que es un valor válido, por tanto actualizamos los índices de valores válidos
            else:
                preValid = nextValid
                nextValidInx += 1
            index += 1
        return result

    @property
    def label(self):
        return 'Average'

        