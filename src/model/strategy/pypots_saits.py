from model.strategy.imputation import Imputation
import numpy as np
from pypots.imputation import SAITS
import os
import pickle

class PyPotsSaits(Imputation):

    def impute(self, df, column, args = None):
        filename = "./saved_models/SAITS_"
        if args:
            filename = filename + args['label']
        filename = filename + "_"+ column + "_model.sav"

        featureCols = ["SDS_P1", "SDS_P2", "BME280_temperature", "BME280_pressure", "BME280_humidity", "lat", "long"]
        dfFeatures = df[featureCols].copy()
        dataArray = dfFeatures.to_numpy()

        seqLen = 10
        X, indices = self.createSequencesWithIndices(dataArray, seqLen)
        dataset = {"X": X}
        #print(f"Total rows: {len(df)}, sequences created: {len(X)}")
        if os.path.exists(filename):
            model = pickle.load(open(filename, 'rb'))
        else:
            model = SAITS(
                n_steps=seqLen,
                n_features=X.shape[2],
                d_model=64,
                d_ffn=128,
                epochs=20,
                n_layers=2,
                n_heads=4,
                d_k=64,
                d_v=64,
            )
            model.fit(dataset)
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

        #print(f"Returned rows: {len(dfImputed)} (exact match to original rows, time preserved)")

        return dfImputed

    def createSequencesWithIndices(self, data, seqLen):
        sequences, indices = [], []
        for i in range(len(data) - seqLen + 1):
            sequences.append(data[i:i + seqLen])
            indices.append(np.arange(i, i + seqLen))
        return np.array(sequences), np.array(indices)

    @property
    def label(self):
        return('PyPotsSaits')
