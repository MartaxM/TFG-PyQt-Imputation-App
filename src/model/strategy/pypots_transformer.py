from model.strategy.imputation import Imputation
import numpy as np
import pandas as pd
from pypots.imputation import Transformer
from pathlib import Path
import os
import pickle

class PyPotsTransformer(Imputation):

    def impute(self, df, column):
        filename = "./model/transformer_model.sav"
        featureCols = ["SDS_P1", "SDS_P2", "BME280_temperature", "BME280_pressure", "BME280_humidity", "lat", "long"]
        dfFeatures = df[featureCols].copy()
        dataArray = dfFeatures.to_numpy()

        seqLen = 10
        X, indices = self.createSequencesWithIndices(dataArray, seqLen)
        dataset = {"X": X}

        if os.path.exists(filename):
            model = pickle.load(open(filename, 'rb'))
        else:
            print('Training model...')
            model = Transformer(
                n_steps=seqLen,
                n_features=X.shape[2],
                d_model=64,
                d_ffn=128,
                n_layers=2,
                n_heads=4,
                d_k=64,
                d_v=64,
                epochs=20,
            )
            model.fit(dataset)
            # Salvar modelo
            filename = './model/transformer_model.sav'
            pickle.dump(model, open(filename, 'wb'))

        XImputed = model.impute(dataset)
        # Recombine sequences into full dataArray shape
        imputedFull = np.zeros_like(dataArray, dtype=float)
        countFull = np.zeros_like(dataArray, dtype=float)

        for seqIdx in range(XImputed.shape[0]):
            for step in range(seqLen):
                rowIdx = indices[seqIdx, step]
                imputedFull[rowIdx] += XImputed[seqIdx, step]
                countFull[rowIdx] += 1

        countFull[countFull == 0] = 1
        imputedFull = imputedFull / countFull

        # Replace all rows with imputed sensor values
        dfImputed = df.copy()
        dfImputed[featureCols] = imputedFull

        # print(f"Returned rows: {len(dfImputed)} (matches original rows, time preserved)")

        return dfImputed

    def createSequencesWithIndices(self, data, seqLen):
        sequences, indices = [], []
        for i in range(len(data) - seqLen + 1):
            sequences.append(data[i:i + seqLen])
            indices.append(np.arange(i, i + seqLen))
        return np.array(sequences), np.array(indices)

    @property
    def label(self):
        return('PyPotsTransformer')
