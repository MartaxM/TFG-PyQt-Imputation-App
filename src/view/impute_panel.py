from PyQt5.QtWidgets import QListWidget,QListWidgetItem,QVBoxLayout, QGroupBox, QAbstractItemView, QPushButton
from PyQt5.QtCore import pyqtSignal
from view.impute_list_item import ImputeListItem, ImputeCoorWidget

class ImputePanel(QGroupBox):
    imputeMethodChanged = pyqtSignal(str,str)
    visibilityChanged = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__('Impute Panel')
        self.layout = QVBoxLayout()
        self.list = QListWidget()
        self.saveBtn = QPushButton('Save to dataset')
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.saveBtn)
        self.setLayout(self.layout)
        self.list.setSelectionMode(QAbstractItemView.NoSelection)

    def createImputationItems(self, imputationMethods):
        P1Widget = ImputeListItem(self.list, 'SDS_P1',imputationMethods)
        P1Widget.selectionChangedSignal.connect(self.imputeMethodChanged)
        P1Widget.visibilityChangedSignal.connect(self.visibilityChanged)
        item1 = QListWidgetItem()
        item1.setSizeHint(P1Widget.sizeHint())
        self.list.addItem(item1)
        self.list.setItemWidget(item1, P1Widget)

        P2Widget = ImputeListItem(self.list, 'SDS_P2',imputationMethods)
        P2Widget.selectionChangedSignal.connect(self.imputeMethodChanged)
        P2Widget.visibilityChangedSignal.connect(self.visibilityChanged)
        item2 = QListWidgetItem()
        item2.setSizeHint(P2Widget.sizeHint())
        self.list.addItem(item2)
        self.list.setItemWidget(item2, P2Widget)

        latWidget = ImputeCoorWidget(self.list, 'lat',imputationMethods)
        latWidget.selectionChangedSignal.connect(self.imputeMethodChanged)
        item3 = QListWidgetItem()
        item3.setSizeHint(latWidget.sizeHint())
        self.list.addItem(item3)
        self.list.setItemWidget(item3, latWidget)

        longWidget = ImputeCoorWidget(self.list, 'long',imputationMethods)
        longWidget.selectionChangedSignal.connect(self.imputeMethodChanged)
        item4 = QListWidgetItem()
        item4.setSizeHint(longWidget.sizeHint())
        self.list.addItem(item4)
        self.list.setItemWidget(item4, longWidget)


