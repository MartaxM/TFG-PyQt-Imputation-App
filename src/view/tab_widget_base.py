from abc import abstractmethod
from PyQt5.QtWidgets import QWidget

class TabWidgetBase(QWidget):
    @abstractmethod
    def addLayer(self, label, df, columns = None):
        pass

    @abstractmethod
    def removeLayer(self, label, columns = None):
        pass

    @abstractmethod
    def renameLayers(self, renamePairs, args = None):
        pass

    @abstractmethod
    def updateViewResult(self, results):
        pass