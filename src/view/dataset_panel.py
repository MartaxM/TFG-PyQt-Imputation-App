from PyQt5.QtWidgets import QListWidget,QListWidgetItem,QVBoxLayout, QGroupBox, QAbstractItemView
from PyQt5.QtCore import pyqtSignal
from view.dataset_list_item import DatasetListItem

class DatasetPanel(QGroupBox):
    visibilityChanged = pyqtSignal(str,bool)
    datasetRemoved = pyqtSignal(str, int)
    removeData = pyqtSignal(str)
    duplicateDataset = pyqtSignal(str)
    correctDataset = pyqtSignal(str)
    renameDataset = pyqtSignal(str, str)

    def __init__(self):
        super().__init__('Datasets')
        self.layout = QVBoxLayout()
        self.dsList = QListWidget()
        #self.addBtn = QPushButton('+')
        self.layout.addWidget(self.dsList)
        #self.layout.addWidget(self.addBtn)
        self.setLayout(self.layout)
        self.dsList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.dsList.itemSelectionChanged.connect(self.enforceSelection)
        self.maxSelection = 1
        self.analysisMode = False
        
    def reloadList(self, list):
        self.dsList.clear()
        for label in list:
            self.addItem(label)

    def deleteCallback(self, listItem):
        widget = self.dsList.itemWidget(listItem)
        listItemIndex = self.dsList.row(listItem)
        self.datasetRemoved.emit(widget.label.text(), listItemIndex)

    def addItem(self, label):
        item = QListWidgetItem()
        itemWidget = DatasetListItem(label, lambda li=item: self.deleteCallback(item), 
                                     self.removeData, self.duplicateDataset, self.correctDataset, self.renameDataset)
        itemWidget.visibilityChangedSignal.connect(self.visibilityChanged)
        # Set size hint
        item.setSizeHint(itemWidget.sizeHint())
        # Add QListWidgetItem into QListWidget
        self.dsList.addItem(item)
        self.dsList.setItemWidget(item, itemWidget)

    def takeItem(self, listItemIndex):
        self.dsList.takeItem(listItemIndex)
    
    def renameItem(self, oldName, newName):
        widget = self.findByLabel(oldName)
        if widget:
            widget.rename(newName)

    def findByLabel(self, label):
        found = None
        for i in range(self.dsList.count()):
            item = self.dsList.item(i)
            widget = self.dsList.itemWidget(item)
            if widget and widget.label.text() == label:
                found = widget
                break
        return found

    def currentItem(self):
        current = self.dsList.currentItem()
        widget = self.dsList.itemWidget(current)
        return widget
    
    def setAnalysisMode(self, setBool):
        self.analysisMode = setBool
        if self.analysisMode:
            self.maxSelection = 2
            items = self.getAllWidgets()
            for item in items:
                item.visibleToggle.hide()
        else:
            self.maxSelection = 1
            items = self.getAllWidgets()
            for item in items:
                item.visibleToggle.show()
            self.enforceSelection()

    def enforceSelection(self):
        selectedItems = self.dsList.selectedItems()
        if len(selectedItems) > self.maxSelection:
            # Deselect second selected item
            lastSelected = selectedItems[0]
            lastSelected.setSelected(False)

    def getAllWidgets(self):
        result = []
        for i in range(self.dsList.count()):
            item = self.dsList.item(i)
            widget = self.dsList.itemWidget(item)
            if widget:
                result.append(widget)
        return result
    
    def selectedItems(self):
        result = []
        selection =  self.dsList.selectedItems()
        for item in selection:
            result.append(self.dsList.itemWidget(item))
        return result
        
    def setState(self, visible, current, analysisMode):
        if self.analysisMode != analysisMode:
            self.setAnalysisMode(analysisMode)
        items = [self.dsList.item(i) for i in range(self.dsList.count())]
        self.dsList.clearSelection()
        if self.analysisMode:
            for item in items:
                widget = self.dsList.itemWidget(item)
                text = widget.label.text()
                if current and text in current:
                    item.setSelected(True)
                else:
                    item.setSelected(False)
        else:
            for item in items:
                widget = self.dsList.itemWidget(item)
                text = widget.label.text() 
                if visible and text in visible:
                    widget.visibleToggle.setChecked(True)
                else:
                    widget.visibleToggle.setChecked(False)
                if current and text == current:
                    item.setSelected(True)
                else:
                    item.setSelected(False)
