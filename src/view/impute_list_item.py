from PyQt5.QtWidgets import QWidget, QHBoxLayout,QLabel,QPushButton,QStyle, QComboBox, QVBoxLayout, QListWidgetItem
from PyQt5.QtCore import pyqtSignal

class ImputeCoorWidget(QWidget):
    selectionChangedSignal = pyqtSignal(str,str)
    def __init__ (self,parentListWidget, lb, imputationMethods):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.parent = parentListWidget
        im = imputationMethods
        self.__label = QLabel(lb)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        self.selector = QComboBox()
        self.selector.addItems(im)
        self.selector.currentTextChanged.connect(self.__handleSelectionChanged)
        self.layout.addWidget(self.__label)
        self.layout.addWidget(self.selector)
    
    @property
    def label(self):
        return self.__label.text()
        
    def __handleSelectionChanged(self, text):
        label = self.__label.text()
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
        self.__label = QLabel(lb)
        self.__visibleToggle = QPushButton(self)
        self.__visibleToggle.setIcon(self.__visibleToggle.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.__visibleToggle.setCheckable(True)
        self.__visibleToggle.setFixedWidth(30)
        self.__visibleToggle.setFlat(True)
        self.__visibleToggle.setStyleSheet(style)
        self.__visibleToggle.toggled.connect(self.__handleVisibilityChanged)

        self.__optionsBtn = QPushButton(self)
        icon = self.__optionsBtn.style().standardIcon(QStyle.SP_TitleBarUnshadeButton)
        self.__optionsBtn.setIcon(icon)
        self.__optionsBtn.setFixedWidth(40)
        self.__optionsBtn.setFlat(True)
        self.__optionsBtn.setStyleSheet(style)
        self.__optionsBtn.clicked.connect(self.openOptions)

        self.layout.addWidget(self.__visibleToggle)
        self.layout.addWidget(self.__label)
        self.layout.addWidget(self.__optionsBtn)

        self.setLayout(self.layout)
    
    @property
    def label(self):
        return self.__label.text()

    def openOptions(self):
        if not self.expanded:
            # Insert detail widget below this item
            index = self.__findIndex()
            if index is None:
                return

            self.detail_item = QListWidgetItem()
            detail_widget = DetailWidget(self.imputationMethods)
            detail_widget.selectionChanged.connect(self.__handleSelectionChanged)
            self.detail_item.setSizeHint(detail_widget.sizeHint())
            self.parent.insertItem(index + 1, self.detail_item)
            self.parent.setItemWidget(self.detail_item, detail_widget)

            self.expanded = True
            icon = self.__optionsBtn.style().standardIcon(QStyle.SP_TitleBarShadeButton)
            self.__optionsBtn.setIcon(icon)

        else:
            # Remove the detail widget
            if self.detail_item:
                row = self.parent.row(self.detail_item)
                self.parent.takeItem(row)
                self.detail_item = None

            self.expanded = False
            icon = self.__optionsBtn.style().standardIcon(QStyle.SP_TitleBarUnshadeButton)
            self.__optionsBtn.setIcon(icon)
        
    def __handleSelectionChanged(self, text):
        label = self.__label.text()
        self.selectionChangedSignal.emit(label,text)

    def __handleVisibilityChanged(self, checked):
        if checked:
            self.__visibleToggle.setIcon(self.__visibleToggle.style().standardIcon(QStyle.SP_DialogYesButton))
        else:
            self.__visibleToggle.setIcon(self.__visibleToggle.style().standardIcon(QStyle.SP_DialogCancelButton))

        label = self.__label.text()
        self.visibilityChangedSignal.emit(label, checked)

    def __findIndex(self):
        for i in range(self.parent.count()):
            if self.parent.itemWidget(self.parent.item(i)) == self:
                return i
        return None
    
    def setVisibilityStatus(self, status):
        self.__visibleToggle.setChecked(status)


