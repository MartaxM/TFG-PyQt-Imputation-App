import sys
import io
import pandas as pd
from model.dataset_list import DatasetList
from PyQt5.QtWidgets import QFileDialog, QDialog

from view.import_dialog import ImportDialog
from view.export_dialog import ExportDialog
from view.remove_dialog import RemoveDialog
from view.correction_dialog import CorrectionDialog

from view.map import Map
from view.plot import Plot
from view.analysis_tab import AnalysisTab

class DatasetControler:
    def __init__(self, model, view, datasetPanel, imputePanel, tabWidget):
        self.model = model
        self.view = view
        self.datasetPanel = datasetPanel
        self.imputePanel = imputePanel
        self.tabWidget = tabWidget
        self.addTab("Plot")
        self.initConnections()
        self.listenToModel()
        self.getImputationMethods()

    def initConnections(self):
        """Connect signals from view to corresponding actions"""
        self.view.openImportDialog.connect(self.openFileDialog)
        self.view.openExportDialog.connect(self.openExportFileDialog)
        self.view.addTabSignal.connect(self.addTab)
        self.datasetPanel.datasetRemoved.connect(self.handleDatasetRemoval)
        self.datasetPanel.removeData.connect(self.openRemoveDialog)
        self.datasetPanel.dsList.itemSelectionChanged.connect(self.handleSelectionChange)
        self.datasetPanel.visibilityChanged.connect(self.handleDSVisibilityChange)
        self.datasetPanel.duplicateDataset.connect(self.model.duplicateDataset)
        self.datasetPanel.correctDataset.connect(self.openCorrectionDialog)
        self.datasetPanel.renameDataset.connect(self.model.renameDataset)
        self.imputePanel.imputeMethodChanged.connect(self.handleImputationChange)
        self.imputePanel.visibilityChanged.connect(self.handleVisibilityChange)
        self.imputePanel.saveBtn.clicked.connect(self.model.convertCurrent)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        self.tabWidget.tabRenamed.connect(self.model.renameTab)
        #self.tabWidget.currentChanged.connect(self.model.changeTab)

    def listenToModel(self):
        """Subscribe to model"""
        self.model.datasetAdded.connect(self.datasetPanel.addItem)
        self.model.datasetAddedToVisible.connect(self.addDFtoView)
        self.model.datasetRemoved.connect(self.removeDataset)
        self.model.datasetChanged.connect(self.addDFtoView)
        self.model.datasetRenamed.connect(self.datasetRenamed)
        self.model.currentTabChanged.connect(self.updateMenu)
        self.model.imputationChanged.connect(self.updateImputation)
        self.model.imputationVisible.connect(self.updateImputationVisibility)
        self.model.resultUpdated.connect(self.updateResult)

    def datasetRenamed(self, oldLabel, renamePairs):
        """
        Dataset was renamed, update view.

        Args:
            oldLabel (str): Old dataset label.
            renamePairs (str): New dataset label.
        """
        self.datasetPanel.renameItem(oldLabel, renamePairs[oldLabel])
        if(self.model.currentTab.type == 'Map'):
            df = {}
            for old, new in renamePairs.items():
                dataset = self.model.getVarResult(new)
                df.update({old : dataset})
            self.tabWidget.currentWidget().renameLayers(renamePairs, df)
        else:
            self.tabWidget.currentWidget().renameLayers(renamePairs)
        return

    def updateResult(self):
        """Update view to match results."""
        result = self.model.getResults()
        self.tabWidget.currentWidget().updateViewResult(result)
    
    def updateImputation(self, var):
        """
        Update view to match imputation method change for a given variable.

        Args:
            var (str): Corresponding variable.
        """
        result = self.model.getVarResult(var)
        if result:
            self.tabWidget.currentWidget().updateViewResult({var:result})
    
    def updateImputationVisibility(self, var, visible):
        """
        Update view to match imputation visibility change for a given variable.

        Args:
            var (str): Corresponding variable.
            visible (bool): Visibility value.
        """
        result = self.model.getVarResult(var)
        if visible and not result.empty:
            self.tabWidget.currentWidget().updateViewResult({var:result})
        else:
            self.tabWidget.currentWidget().removeLayer(var)

    def updateMenu(self,index):
        """
        Update menu based on the current tab.

        Args:
            index (int): Tab index
        """
        self.tabWidget.setCurrentIndex(index)
        tabInfo = self.model.currentTab
        visible = tabInfo.visible
        current = tabInfo.selection
        if tabInfo.type == 'AnalysisTab':
            self.datasetPanel.setState(visible, current, True)
            self.imputePanel.setVisible(False)
        else:
            self.datasetPanel.setState(visible, current, False)
            self.imputePanel.setVisible(True)

    def closeTab(self, index):
        """
        Close tab.

        Args:
            index (int): Tab index.
        """
        self.tabWidget.removeTab(index)
        self.model.removeTab(index)

    def addTab(self, label):
        tab = Plot()
        if label == "Analysis":
            tab = AnalysisTab()
        elif label == "Map":
            tab = Map()
        self.tabWidget.addTab(tab, label)
        if label == "Analysis":
            self.model.addTab( label, tab.__class__.__name__, 2)
        else:
            self.model.addTab( label, tab.__class__.__name__)
        return

    def handleImputationChange(self, label, selection):
        self.model.changeImputationSelection(label, selection)

    def handleVisibilityChange(self, label, checked):
        self.model.changeImputationVisiblity(label, checked)

    def handleDSVisibilityChange(self, label, checked):
        self.model.changeDatasetVisiblity(label, checked)

    def handleSelectionChange(self):
        """Handle selected dataset change"""
        if type(self.tabWidget) is AnalysisTab:
            selection = self.datasetPanel.selectedItems()
            labels = []
            for item in selection:
                label = item.label.text()
                labels.append(label)
                self.model.setCurrent(labels)
        else:
            widget = self.datasetPanel.currentItem()
            if(widget):
                labelText = widget.label.text()
                self.model.setCurrent(labelText)
                self.imputePanel.setVisible(True)
            else:
                self.imputePanel.setVisible(False)

    def getImputationMethods(self):
        imputationMethods = list(self.model.imputationMethods.keys())
        self.imputePanel.createImputationItems(imputationMethods)

    def removeDataset(self, label):
        self.tabWidget.currentWidget().removeLayer(label)

    def handleDatasetRemoval(self,label, listItem = None):
        if self.model.removeDataset(label):
            self.datasetPanel.takeItem(listItem)

    def addDFtoView(self, label):
        visible = self.model.currentTab.visible
        if label in visible:
            df = self.model.datasets[label]
            self.tabWidget.currentWidget().addLayer(label, df, 'SDS_P1')

    def openFileDialog(self):
        """Open file import dialog and load selected files into model"""
        file_dialog = QFileDialog(self.view)
        file_dialog.setWindowTitle("Open File")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        selected_files = None

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if(len(selected_files) > 1):
                importDialog = ImportDialog(selected_files)
                if importDialog.exec() == QDialog.Accepted:
                    selection = importDialog.getSelection()
                    if selection['multiple'] == True:
                        for file in selected_files:
                            self.model.loadFromCSV(file)
                    else:
                        self.model.loadFuseFromCSVs(selected_files)
            else:
                self.model.loadFromCSV(selected_files[0])
    
    def openExportFileDialog(self):
        """Open export file dialog and export as cvs files selected datasets"""
        dialog = ExportDialog(self.model.datasets)

        if dialog.exec() == QDialog.Accepted:
            selectedDatasets, selectedOption = dialog.getSelection()
            filter = "csv(*.csv)"
            file_dialog = QFileDialog(self.view)
            file_dialog.setWindowTitle("Save to File")
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
            selected_file = None
            if file_dialog.exec():
                selected_file = file_dialog.selectedFiles()[0]
                if selectedOption == 'One':
                    self.model.saveFuseToCSV(selectedDatasets, selected_file)
                else:
                    self.model.saveToCSV(selectedDatasets, selected_file)
                #print("Estamos guardando")

    def openRemoveDialog(self, label):
        removeDialog = RemoveDialog(self.model.datasets[label])
        if removeDialog.exec() ==  QDialog.Accepted:
            selection = removeDialog.getSelection()
            if selection['mode'] == 'percent':
                self.model.removePercent(label, selection['value'])
            elif selection['mode'] == 'interval':
                self.model.removeInterval(label, selection['inverted'],selection['start'], selection['end'])

    def openCorrectionDialog(self, label):
        correctionDialog = CorrectionDialog()
        if correctionDialog.exec() == QDialog.Accepted:
            substract, division = correctionDialog.getOperands()
            if substract and division:
                self.model.applyCorrection(label,substract,division)