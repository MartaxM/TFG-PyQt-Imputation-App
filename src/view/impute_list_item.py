from PyQt5.QtWidgets import QWidget, QHBoxLayout,QLabel,QPushButton,QStyle, QComboBox, QVBoxLayout, QListWidgetItem
from PyQt5.QtCore import pyqtSignal

class ImputeCoorWidget(QWidget):
    selectionChangedSignal = pyqtSignal(str,str)
    def __init__ (self,parentListWidget, lb, imputationMethods):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.parent = parentListWidget
        im = imputationMethods
        self.label = QLabel(lb)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        self.selector = QComboBox()
        self.selector.addItems(im)
        self.selector.currentTextChanged.connect(self.handleSelectionChanged)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.selector)
        
    def handleSelectionChanged(self, text):
        label = self.label.text()
        self.selectionChangedSignal.emit(label,text)

class DetailWidget(QWidget):
    selectionChanged = pyqtSignal(str)
    def __init__(self, imputationMethods):
        super().__init__()
        layout = QVBoxLayout()
        selector = QComboBox()
        selector.addItems(imputationMethods)
        selector.currentTextChanged.connect(self.selectionChanged)
        layout.addWidget(selector)
        self.setLayout(layout)

class ImputeListItem(QWidget):
    selectionChangedSignal = pyqtSignal(str,str)
    visibilityChangedSignal = pyqtSignal(str,bool)
    def __init__ (self,parentListWidget, lb, imputationMethods):
        super().__init__()
        style = """
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.05);  /* Optional subtle hover */
            }
        """
        self.layout = QHBoxLayout()
        self.parent = parentListWidget
        self.imputationMethods = imputationMethods
        self.expanded = False
        self.label = QLabel(lb)
        self.visibleToggle = QPushButton(self)
        self.visibleToggle.setIcon(self.visibleToggle.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.visibleToggle.setCheckable(True)
        self.visibleToggle.setFixedWidth(30)
        self.visibleToggle.setFlat(True)
        self.visibleToggle.setStyleSheet(style)
        self.visibleToggle.toggled.connect(self.handleVisibilityChanged)

        self.optionsBtn = QPushButton(self)
        icon = self.optionsBtn.style().standardIcon(QStyle.SP_TitleBarUnshadeButton)
        self.optionsBtn.setIcon(icon)
        self.optionsBtn.setFixedWidth(40)
        self.optionsBtn.setFlat(True)
        self.optionsBtn.setStyleSheet(style)
        self.optionsBtn.clicked.connect(self.openOptions)

        self.layout.addWidget(self.visibleToggle)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.optionsBtn)

        self.setLayout(self.layout)
    
    def openOptions(self):
        if not self.expanded:
            # Insert detail widget below this item
            index = self._findIndex()
            if index is None:
                return

            self.detail_item = QListWidgetItem()
            detail_widget = DetailWidget(self.imputationMethods)
            detail_widget.selectionChanged.connect(self.handleSelectionChanged)
            self.detail_item.setSizeHint(detail_widget.sizeHint())
            self.parent.insertItem(index + 1, self.detail_item)
            self.parent.setItemWidget(self.detail_item, detail_widget)

            self.expanded = True
            icon = self.optionsBtn.style().standardIcon(QStyle.SP_TitleBarShadeButton)
            self.optionsBtn.setIcon(icon)

        else:
            # Remove the detail widget
            if self.detail_item:
                row = self.parent.row(self.detail_item)
                self.parent.takeItem(row)
                self.detail_item = None

            self.expanded = False
            icon = self.optionsBtn.style().standardIcon(QStyle.SP_TitleBarUnshadeButton)
            self.optionsBtn.setIcon(icon)
        
    def handleSelectionChanged(self, text):
        label = self.label.text()
        self.selectionChangedSignal.emit(label,text)

    def handleVisibilityChanged(self, checked):
        if checked:
            self.visibleToggle.setIcon(self.visibleToggle.style().standardIcon(QStyle.SP_DialogYesButton))
        else:
            self.visibleToggle.setIcon(self.visibleToggle.style().standardIcon(QStyle.SP_DialogCancelButton))

        label = self.label.text()
        self.visibilityChangedSignal.emit(label, checked)

    def _findIndex(self):
        for i in range(self.parent.count()):
            if self.parent.itemWidget(self.parent.item(i)) == self:
                return i
        return None


