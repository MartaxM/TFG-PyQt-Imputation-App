from PyQt5.QtWidgets import (
    QApplication, QTabWidget, QLineEdit,
)
from PyQt5.QtCore import pyqtSignal, QEvent, Qt
import sys

class RenamableTabWidget(QTabWidget):
    tabRenamed = pyqtSignal(int,str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setVisible(False)
        self.lineEdit.setWindowFlags(Qt.Popup)
        self.lineEdit.editingFinished.connect(self.finishRenaming)
        self.tabBar().installEventFilter(self)
        QApplication.instance().installEventFilter(self)
    
    def eventFilter(self, obj, event):
        if obj == self.tabBar() and event.type() == event.MouseButtonDblClick:
            index = self.tabBar().tabAt(event.pos())
            if index != -1:
                self.startRenaming(index)
            return True
        
        if hasattr(self, "lineEdit") and self.lineEdit.isVisible():
            if event.type() == QEvent.MouseButtonPress:
                if not self.lineEdit.geometry().contains(self.mapFromGlobal(event.globalPos())):
                    self.cancelRenaming()
                    return True
                
        return super().eventFilter(obj, event)

    def startRenaming(self, index):
        rect = self.tabBar().tabRect(index)
        self.renamingIndex = index
        self.lineEdit.setText(self.tabText(index))
        self.lineEdit.setGeometry(self.tabBar().mapToGlobal(rect.topLeft()).x(),
                                   self.tabBar().mapToGlobal(rect.topLeft()).y(),
                                   rect.width(), rect.height())
        self.lineEdit.setVisible(True)
        self.lineEdit.setFocus()
        self.lineEdit.selectAll()

    def finishRenaming(self):
        newName = self.lineEdit.text().strip()
        if newName:
            self.setTabText(self.renamingIndex, newName)
        self.lineEdit.setVisible(False)
        self.tabRenamed.emit(self.renamingIndex,newName)
    
    def cancelRenaming(self):
        self.lineEdit.setVisible(False)
