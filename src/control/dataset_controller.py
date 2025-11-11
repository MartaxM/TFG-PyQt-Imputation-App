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
        self.__model = model
        self.__view = view
        self.__datasetPanel = datasetPanel
        self.__imputePanel = imputePanel
        self.__tabWidget = tabWidget
        self.addTab("Plot")
        self.initConnections()
        self.listenToModel()
        self.getImputationMethods()

    def initConnections(self):
        """Connect signals from view to corresponding actions"""
        self.__view.openImportDialog.connect(self.openFileDialog)
        self.__view.openExportDialog.connect(self.openExportFileDialog)
        self.__view.addTabSignal.connect(self.addTab)
        self.__datasetPanel.datasetRemoved.connect(self.handleDatasetRemoval)
        self.__datasetPanel.removeData.connect(self.openRemoveDialog)
        self.__datasetPanel.dsList.itemSelectionChanged.connect(self.handleSelectionChange)
        self.__datasetPanel.datasetVisibilityChanged.connect(self.handleDSVisibilityChange)
        self.__datasetPanel.duplicateDataset.connect(self.__model.duplicateDataset)
        self.__datasetPanel.correctDataset.connect(self.openCorrectionDialog)
        self.__datasetPanel.renameDataset.connect(self.__model.renameDataset)
        self.__imputePanel.imputeMethodChanged.connect(self.handleImputationChange)
        self.__imputePanel.imputeVisibilityChanged.connect(self.handleVisibilityChange)
        self.__imputePanel.saveBtn.clicked.connect(self.__model.convertCurrent)
        self.__tabWidget.tabCloseRequested.connect(self.closeTab)
        self.__tabWidget.tabRenamed.connect(self.__model.renameTab)
        self.__tabWidget.currentChanged.connect(self.__model.changeTab)

    def listenToModel(self):
        """Subscribe to model"""
        self.__model.datasetAdded.connect(self.__datasetPanel.addItem)
        self.__model.datasetVisilityChanged.connect(self.changeDatasetVisibility)
        self.__model.datasetRemoved.connect(self.removeDataset)
        self.__model.datasetRenamed.connect(self.datasetRenamed)
        self.__model.clearResult.connect(self.removeResult)
        self.__model.currentTabChanged.connect(self.updateMenu)
        self.__model.imputationChanged.connect(self.updateImputation)
        self.__model.imputationVisible.connect(self.updateImputationVisibility)
        self.__model.resultUpdated.connect(self.updateResult)

    def datasetRenamed(self, oldLabel, renamePairs):
        """
        Dataset was renamed, update view.

        Args:
            oldLabel (str): Old dataset label.
            renamePairs (str): New dataset label.
        """
        self.__datasetPanel.renameItem(oldLabel, renamePairs[oldLabel])
        df = {}
        for old, new in renamePairs.items():
            dataset = self.__model.getDataset(new)
            df.update({old : dataset})

        args = {
            'df' : df,
            'columns' : self.__model.variables
        }

        for i in range(self.__tabWidget.count()):
            self.__tabWidget.widget(i).renameLayers(renamePairs, args = args)
        return

    def updateResult(self):
        """Update view to match results."""
        result = self.__model.getResults()
        self.__tabWidget.currentWidget().updateViewResult(result)
    
    def updateImputation(self, var):
        """
        Update view to match imputation method change for a given variable.

        Args:
            var (str): Corresponding variable.
        """
        result = self.__model.getVarResult(var)
        if not result is None:
            self.__tabWidget.currentWidget().updateViewResult({var:result})
    
    def updateImputationVisibility(self, var, visible):
        """
        Update view to match imputation visibility change for a given variable.

        Args:
            var (str): Corresponding variable.
            visible (bool): Visibility value.
        """
        result = self.__model.getVarResult(var)
        if visible and not result is None:
            self.__tabWidget.currentWidget().updateViewResult({var:result})
        else:
            self.__tabWidget.currentWidget().removeLayer(var)

    def updateMenu(self,index):
        """
        Update menu based on the current tab.

        Args:
            index (int): Tab index
        """
        if index < 0:
            self.__imputePanel.hide()
            self.__datasetPanel.setMaxSelection(0)
            self.__datasetPanel.setVisibilityControllable(False)
        else:
            self.__tabWidget.setCurrentIndex(index)
            tabInfo = self.__model.currentTab
            visible = tabInfo.visible
            current = tabInfo.selection
            visibleImputation = tabInfo.getVisibleImputationVariables()
            self.__datasetPanel.show()
            if tabInfo.type == 'AnalysisTab':
                self.__datasetPanel.setState(visible, current, False, 2)
                self.__imputePanel.hide()
            else:
                self.__datasetPanel.setState(visible, current, True, 1)
                self.__imputePanel.show()
                self.__imputePanel.setState(visibleImputation)

    def closeTab(self, index):
        """
        Close tab.

        Args:
            index (int): Tab index.
        """
        self.__tabWidget.removeTab(index)
        self.__model.removeTab(index)

    def addTab(self, label):
        tab = Plot()
        if label == "Analysis":
            tab = AnalysisTab()
        elif label == "Map":
            tab = Map()
        self.__tabWidget.addTab(tab, label)
        if label == "Analysis":
            self.__model.addTab( label, tab.__class__.__name__, 2)
        else:
            self.__model.addTab( label, tab.__class__.__name__)
        
        return

    def handleImputationChange(self, label, selection):
        self.__model.changeImputationSelection(label, selection)

    def handleVisibilityChange(self, label, checked):
        self.__model.changeImputationVisiblity(label, checked)

    def handleDSVisibilityChange(self, label, checked):
        self.__model.changeDatasetVisiblity(label, checked)

    def handleSelectionChange(self):
        """Handle selected dataset change"""
        if self.__model.currentTab.type == 'AnalysisTab':
            selection = self.__datasetPanel.selectedItems()
            labels = []
            for item in selection:
                label = item.label
                labels.append(label)
                self.__model.setCurrent(labels)
        else:
            widget = self.__datasetPanel.currentItem()
            if(widget):
                labelText = widget.label
                self.__model.setCurrent(labelText)

    def getImputationMethods(self):
        imputationMethods = list(self.__model.imputationMethods.keys())
        self.__imputePanel.createImputationItems(self.__model.variables, self.__model.alwaysVisibleVariables, imputationMethods)

    def removeResult(self, label):
        self.__tabWidget.currentWidget().removeLayer(label)

    def removeDataset(self, label, columns):
        for i in range(self.__tabWidget.count()):
            self.__tabWidget.currentWidget().removeLayer(label, columns)

    def handleDatasetRemoval(self,label, listItem = None):
        if self.__model.removeDataset(label):
            self.__datasetPanel.takeItem(listItem)

    def changeDatasetVisibility(self, label, visiblityStatus):
        df = self.__model.getDataset(label)
        if not df is None:
            columns = set(self.__model.variables).intersection(df.columns)
            if visiblityStatus:
                self.__tabWidget.currentWidget().addLayer(label, df, columns)
            else:
                self.__tabWidget.currentWidget().removeLayer(label, columns)

    def openFileDialog(self):
        """Open file import dialog and load selected files into model"""
        file_dialog = QFileDialog(self.__view)
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
                            self.__model.loadFromCSV(file)
                    else:
                        self.__model.loadFuseFromCSVs(selected_files)
            else:
                self.__model.loadFromCSV(selected_files[0])
    
    def openExportFileDialog(self):
        """Open export file dialog and export as cvs files selected datasets"""
        dialog = ExportDialog(self.__model.datasets)

        if dialog.exec() == QDialog.Accepted:
            selectedDatasets, selectedOption = dialog.getSelection()
            file_dialog = QFileDialog(self.__view)
            file_dialog.setWindowTitle("Save to File")
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
            selected_file = None
            if file_dialog.exec():
                selected_file = file_dialog.selectedFiles()[0]
                if selectedOption == 'One':
                    self.__model.saveFuseToCSV(selectedDatasets, selected_file)
                else:
                    self.__model.saveToCSV(selectedDatasets, selected_file)
                    
    def openRemoveDialog(self, label):
        removeDialog = RemoveDialog(self.__model.datasets[label])
        if removeDialog.exec() ==  QDialog.Accepted:
            selection = removeDialog.getSelection()
            if selection['mode'] == 'percent':
                self.__model.removePercent(label, selection['value'])
            elif selection['mode'] == 'interval':
                self.__model.removeInterval(label, selection['inverted'],selection['start'], selection['end'])

    def openCorrectionDialog(self, label):
        correctionDialog = CorrectionDialog()
        if correctionDialog.exec() == QDialog.Accepted:
            substract, division = correctionDialog.getOperands()
            if substract and division:
                self.__model.applyCorrection(label,substract,division)