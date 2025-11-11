from PyQt5.QtWidgets import QWidget, QHBoxLayout,QLabel,QPushButton,QStyle, QLineEdit, QApplication, QAction, QMenu
from PyQt5.QtCore import pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QCursor

class DatasetListItem(QWidget):
    visibilityChangedSignal = pyqtSignal(str,bool)

    def __init__ (self, lb, deleteCallback, removeSignal, duplicateSignal, correctionSignal, renameSignal,visible = False, toggleable = True):
        super().__init__()
        self.layout = QHBoxLayout()
        style = """
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.05);  /* Optional subtle hover */
            }
        """
        self.deleteCallback = deleteCallback
        self.removeSignal = removeSignal
        self.duplicateSignal = duplicateSignal
        self.correctionSignal = correctionSignal
        self.renameSignal = renameSignal

        # Widgets
        self.__label = QLabel(lb)
        self.__visibleToggle = QPushButton(self)
        self.__visibleToggle.setCheckable(True)
        self.__visibleToggle.setChecked(visible)
        self.__visibleToggle.setFixedWidth(30)
        self.__visibleToggle.setFlat(True)
        visibleIcon = self.__visibleToggle.style().standardIcon(QStyle.SP_DialogCancelButton)
        self.__visibleToggle.setIcon(visibleIcon)
        self.__visibleToggle.setStyleSheet(style)
        if not toggleable:
            self.__visibleToggle.hide()

        self.__optionsBtn = QPushButton(self)
        optionsIcon = self.__optionsBtn.style().standardIcon(QStyle.SP_ToolBarVerticalExtensionButton)
        self.__optionsBtn.setFlat(True)
        self.__optionsBtn.setIcon(optionsIcon)
        self.__optionsBtn.setFixedWidth(30)
        self.__optionsBtn.setStyleSheet(style)
        
        # Layout
        self.layout.addWidget(self.__visibleToggle)
        self.layout.addWidget(self.__label)
        self.layout.addWidget(self.__optionsBtn)
        
        self.setLayout(self.layout)
        self.__visibleToggle.toggled.connect(self.__handleVisibilityChanged)
        self.__optionsBtn.clicked.connect(self._openMenu)

        # Renaming set up
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setVisible(False)
        self.lineEdit.setWindowFlags(Qt.Popup)
        self.lineEdit.editingFinished.connect(self.finishRenaming)
        self.installEventFilter(self)
        QApplication.instance().installEventFilter(self)

    @property
    def label(self):
        return self.__label.text()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self._openMenu()

        super().mousePressEvent(event)

    def _openMenu(self):
        menu = QMenu(self.__optionsBtn)
        duplicateAction = QAction("&Duplicate", self.__optionsBtn)
        duplicateAction.triggered.connect(self.__triggerDuplicateSignal)
        removeAction = QAction("&Remove data", self.__optionsBtn)
        removeAction.triggered.connect(self.__triggerRemoveSignal)
        applyCorrectionAction = QAction("&Apply correction", self.__optionsBtn)
        applyCorrectionAction.triggered.connect(self.__triggerCorrectionSignal)
        renameAction = QAction("&Rename", self.__optionsBtn)
        renameAction.triggered.connect(self.startRenaming)
        deleteAction = QAction("&Delete", self.__optionsBtn)
        deleteAction.triggered.connect(self.deleteCallback)

        menu.addAction(removeAction)
        menu.addAction(duplicateAction)
        menu.addAction(applyCorrectionAction)
        menu.addAction(renameAction)
        menu.addAction(deleteAction)
        menu.exec(QCursor.pos())

    def __triggerRemoveSignal(self):
        self.removeSignal.emit(self.__label.text())
    
    def __triggerDuplicateSignal(self):
        self.duplicateSignal.emit(self.__label.text())

    def __triggerCorrectionSignal(self):
        self.correctionSignal.emit(self.__label.text())

    def __handleVisibilityChanged(self, checked):
        if checked:
            self.__visibleToggle.setIcon(self.__visibleToggle.style().standardIcon(QStyle.SP_DialogYesButton))
        else:
            self.__visibleToggle.setIcon(self.__visibleToggle.style().standardIcon(QStyle.SP_DialogCancelButton))
    
        label = self.__label.text()
        self.visibilityChangedSignal.emit(label, checked)

    def eventFilter(self, obj, event):
        if obj == self.__label and event.type() == event.MouseButtonDblClick:
            self.startRenaming()
            return True
        
        if self.lineEdit.isVisible():
            if event.type() == QEvent.MouseButtonPress:
                if not self.lineEdit.geometry().contains(self.mapFromGlobal(event.globalPos())):
                    self.cancelRenaming()
                    return True
                
        return super().eventFilter(obj, event)

    def startRenaming(self):
        rect = self.__label.rect()
        self.lineEdit.setText(self.__label.text())
        self.lineEdit.setGeometry(self.__label.mapToGlobal(rect.topLeft()).x(),
                                    self.__label.mapToGlobal(rect.topLeft()).y(),
                                    rect.width(), rect.height())
        self.lineEdit.setVisible(True)
        self.lineEdit.setFocus()
        self.lineEdit.selectAll()

    def finishRenaming(self):
        if not self.lineEdit.isModified():
            return
        self.lineEdit.setModified(False)
        newName = self.lineEdit.text().strip()
        oldName = self.__label.text()
        if newName and newName != oldName:
            self.renameSignal.emit(oldName,newName)
        self.lineEdit.setVisible(False)

    def cancelRenaming(self):
        self.lineEdit.setVisible(False)
    
    def rename(self, newName):
        self.__label.setText(newName)

    def visibilityControllable(self, status):
        if status:
            self.__visibleToggle.show()
        else: 
            self.__visibleToggle.hide()

    def setVisibilityStatus(self, status):
        self.__visibleToggle.setChecked(status)
        #self.__handleVisibilityChanged(status)