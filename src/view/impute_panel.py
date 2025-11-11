from PyQt5.QtWidgets import QListWidget,QListWidgetItem,QVBoxLayout, QGroupBox, QAbstractItemView, QPushButton
from PyQt5.QtCore import pyqtSignal
from view.impute_list_item import ImputeListItem, ImputeCoorWidget

class ImputePanel(QGroupBox):
    imputeMethodChanged = pyqtSignal(str,str)
    imputeVisibilityChanged = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__('Impute Panel')
        self.layout = QVBoxLayout()
        self.list = QListWidget()
        self.saveBtn = QPushButton('Save to dataset')
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.saveBtn)
        self.setLayout(self.layout)
        self.list.setSelectionMode(QAbstractItemView.NoSelection)

    def createImputationItems(self, toggleableVariables, alwaysVisibleVariables, imputationMethods):
        for var in toggleableVariables:
            widget = ImputeListItem(self.list, var,imputationMethods)
            widget.selectionChangedSignal.connect(self.imputeMethodChanged)
            widget.visibilityChangedSignal.connect(self.imputeVisibilityChanged)
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.list.addItem(item)
            self.list.setItemWidget(item, widget)

        for var in alwaysVisibleVariables:
            widget = ImputeCoorWidget(self.list, var ,imputationMethods)
            widget.selectionChangedSignal.connect(self.imputeMethodChanged)
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.list.addItem(item)
            self.list.setItemWidget(item, widget)

    def setState(self, visibleVariables):
        items = [self.list.item(i) for i in range(self.list.count())]
        self.blockSignals(True)
        for item in items:
            widget = self.list.itemWidget(item)
            if isinstance(widget, ImputeListItem):
                text = widget.label
                if text in visibleVariables:
                    widget.setVisibilityStatus(True)
                else:
                    widget.setVisibilityStatus(False)

        self.blockSignals(False)