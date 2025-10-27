from abc import abstractmethod
from PyQt5.QtWidgets import QWidget

class TabWidgetBase(QWidget):
    @abstractmethod
    def addLayer(self, label, df, column = None):
        pass

    @abstractmethod
    def removeLayer(self, label, column = None):
        pass

    @abstractmethod
    def reload(self, df_list, column = None):
        pass

    @abstractmethod
    def renameLayers(self, renamePairs, df = None):
        pass

    @abstractmethod
    def updateViewResult(self, results):
        pass