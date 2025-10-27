from abc import ABC, abstractmethod

class Imputation(ABC):
    @abstractmethod
    def impute(self, df, column):
        pass

    @property
    @abstractmethod
    def label(self):
        pass