from PyQt5.QtWidgets import QWidget, QHBoxLayout,QLabel,QPushButton,QStyle, QLineEdit, QApplication, QAction, QMenu
from PyQt5.QtCore import pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QCursor

class DatasetListItem(QWidget):
    visibilityChangedSignal = pyqtSignal(str,bool)

    def __init__ (self, lb, deleteCallback, removeSignal, duplicateSignal, correctionSignal, renameSignal,visible = False):
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
        self.label = QLabel(lb)
        self.visibleToggle = QPushButton(self)
        self.visibleToggle.setCheckable(True)
        self.visibleToggle.setChecked(visible)
        self.visibleToggle.setFixedWidth(30)
        self.visibleToggle.setFlat(True)
        visibleIcon = self.visibleToggle.style().standardIcon(QStyle.SP_DialogCancelButton)
        self.visibleToggle.setIcon(visibleIcon)
        self.visibleToggle.setStyleSheet(style)

        self.optionsBtn = QPushButton(self)
        optionsIcon = self.optionsBtn.style().standardIcon(QStyle.SP_ToolBarVerticalExtensionButton)
        self.optionsBtn.setFlat(True)
        self.optionsBtn.setIcon(optionsIcon)
        self.optionsBtn.setFixedWidth(30)
        self.optionsBtn.setStyleSheet(style)
        
        # Layout
        self.layout.addWidget(self.visibleToggle)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.optionsBtn)
        
        self.setLayout(self.layout)
        self.visibleToggle.toggled.connect(self.handleVisibilityChanged)
        self.optionsBtn.clicked.connect(self._openMenu)

        # Renaming set up
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setVisible(False)
        self.lineEdit.setWindowFlags(Qt.Popup)
        self.lineEdit.editingFinished.connect(self.finishRenaming)
        self.installEventFilter(self)
        QApplication.instance().installEventFilter(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self._openMenu()

        super().mousePressEvent(event)

    def _openMenu(self):
        menu = QMenu(self.optionsBtn)
        duplicateAction = QAction("&Duplicate", self.optionsBtn)
        duplicateAction.triggered.connect(self._triggerDuplicateSignal)
        removeAction = QAction("&Remove data", self.optionsBtn)
        removeAction.triggered.connect(self._triggerRemoveSignal)
        applyCorrectionAction = QAction("&Apply correction", self.optionsBtn)
        applyCorrectionAction.triggered.connect(self._triggerCorrectionSignal)
        renameAction = QAction("&Rename", self.optionsBtn)
        renameAction.triggered.connect(self.startRenaming)
        deleteAction = QAction("&Delete", self.optionsBtn)
        deleteAction.triggered.connect(self.deleteCallback)

        menu.addAction(removeAction)
        menu.addAction(duplicateAction)
        menu.addAction(applyCorrectionAction)
        menu.addAction(renameAction)
        menu.addAction(deleteAction)
        menu.exec(QCursor.pos())

    def _triggerRemoveSignal(self):
        self.removeSignal.emit(self.label.text())
    
    def _triggerDuplicateSignal(self):
        self.duplicateSignal.emit(self.label.text())

    def _triggerCorrectionSignal(self):
        self.correctionSignal.emit(self.label.text())

    def handleVisibilityChanged(self, checked):
        if checked:
            self.visibleToggle.setIcon(self.visibleToggle.style().standardIcon(QStyle.SP_DialogYesButton))
        else:
            self.visibleToggle.setIcon(self.visibleToggle.style().standardIcon(QStyle.SP_DialogCancelButton))
    
        label = self.label.text()
        self.visibilityChangedSignal.emit(label, checked)

    def eventFilter(self, obj, event):
        if obj == self.label and event.type() == event.MouseButtonDblClick:
            self.startRenaming()
            return True
        
        if self.lineEdit.isVisible():
            if event.type() == QEvent.MouseButtonPress:
                if not self.lineEdit.geometry().contains(self.mapFromGlobal(event.globalPos())):
                    self.cancelRenaming()
                    return True
                
        return super().eventFilter(obj, event)

    def startRenaming(self):
        rect = self.label.rect()
        self.lineEdit.setText(self.label.text())
        self.lineEdit.setGeometry(self.label.mapToGlobal(rect.topLeft()).x(),
                                    self.label.mapToGlobal(rect.topLeft()).y(),
                                    rect.width(), rect.height())
        self.lineEdit.setVisible(True)
        self.lineEdit.setFocus()
        self.lineEdit.selectAll()

    def finishRenaming(self):
        if not self.lineEdit.isModified():
            return
        self.lineEdit.setModified(False)
        newName = self.lineEdit.text().strip()
        oldName = self.label.text()
        if newName and newName != oldName:
            self.renameSignal.emit(oldName,newName)
        self.lineEdit.setVisible(False)

    def cancelRenaming(self):
        self.lineEdit.setVisible(False)
    
    def rename(self, newName):
        self.label.setText(newName)
