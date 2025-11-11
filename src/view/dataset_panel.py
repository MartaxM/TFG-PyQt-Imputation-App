from PyQt5.QtWidgets import QListWidget,QListWidgetItem,QVBoxLayout, QGroupBox, QAbstractItemView, QApplication
from PyQt5.QtCore import pyqtSignal
from view.dataset_list_item import DatasetListItem

class DatasetPanel(QGroupBox):
    datasetVisibilityChanged = pyqtSignal(str,bool)
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
        self.dsList.itemSelectionChanged.connect(self.__enforceSelection)
        self.__maxSelection = 1
        self.__visibilityControllable = True
        
    def reloadList(self, list):
        self.dsList.clear()
        for label in list:
            self.addItem(label)

    def __deleteCallback(self, listItem):
        widget = self.dsList.itemWidget(listItem)
        listItemIndex = self.dsList.row(listItem)
        self.datasetRemoved.emit(widget.label, listItemIndex)

    def addItem(self, label):
        item = QListWidgetItem()
        itemWidget = DatasetListItem(label, lambda li=item: self.__deleteCallback(item), 
                                     self.removeData, self.duplicateDataset, self.correctDataset, self.renameDataset)
        
        if not self.__visibilityControllable:
            itemWidget.visibilityControllable(False)
            
        itemWidget.visibilityChangedSignal.connect(self.datasetVisibilityChanged)
        # Set size hint
        item.setSizeHint(itemWidget.sizeHint())
        # Add QListWidgetItem into QListWidget
        self.dsList.addItem(item)
        self.dsList.setItemWidget(item, itemWidget)

    def takeItem(self, listItemIndex):
        self.dsList.takeItem(listItemIndex)
    
    def renameItem(self, oldName, newName):
        widget = self.__findBylabel(oldName)
        if widget:
            widget.rename(newName)

    def __findBylabel(self, label):
        found = None
        for i in range(self.dsList.count()):
            item = self.dsList.item(i)
            widget = self.dsList.itemWidget(item)
            if widget and widget.label == label:
                found = widget
                break
        return found

    def currentItem(self):
        current = self.dsList.currentItem()
        widget = self.dsList.itemWidget(current)
        return widget

    def __enforceSelection(self):
        selectedItems = self.dsList.selectedItems()
        
        if len(selectedItems) > self.__maxSelection:
            self.dsList.blockSignals(True)
            lastSelected = selectedItems[0]
            lastSelected.setSelected(False)
            self.dsList.blockSignals(False)

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
        
    def setVisibilityControllable(self, controllable):
        if not controllable == self.__visibilityControllable:
            self.__visibilityControllable = controllable
            items = self.getAllWidgets()
            if controllable:    
                for item in items:
                    item.visibilityControllable(True)
            else:
                for item in items:
                    item.visibilityControllable(False)

    def setMaxSelection(self, maxSelection):
        if not maxSelection == self.__maxSelection:
            self.__maxSelection = maxSelection
            if maxSelection == 0:
                self.dsList.setSelectionMode(QAbstractItemView.NoSelection)
            else:
                self.dsList.setSelectionMode(QAbstractItemView.MultiSelection)
                self.__enforceSelection()

    def setState(self, visible, current, visibilityControllable, maxSelection):
        self.setVisibilityControllable(visibilityControllable)
        self.setMaxSelection(maxSelection)
        items = [self.dsList.item(i) for i in range(self.dsList.count())]
        self.dsList.blockSignals(True)
        for item in items:
            widget = self.dsList.itemWidget(item)
            text = widget.label
            if self.__visibilityControllable and text in visible:
                widget.setVisibilityStatus(True)
            else:
                widget.setVisibilityStatus(False)
                widget = self.dsList.itemWidget(item)
                text = widget.label
                if current and text in current:
                    item.setSelected(True)
                else:
                    item.setSelected(False)
        self.dsList.blockSignals(False)

