from PyQt5.QtCore import QObject, pyqtSignal
import pandas as pd
import time
import os
from pathlib import Path
from model.tab_info import TabInfo
from model.remove import *

class DatasetList(QObject):
    datasetAdded = pyqtSignal(str)
    datasetVisilityChanged = pyqtSignal(str, bool)
    clearResult = pyqtSignal(str)
    datasetRemoved = pyqtSignal(str, list)
    datasetRenamed = pyqtSignal(str, dict)
    currentTabChanged = pyqtSignal(int)
    resultUpdated = pyqtSignal()
    imputationChanged = pyqtSignal(str)
    imputationVisible = pyqtSignal(str, bool)

    def __init__(self, imputationMethods, variables = None, alwaysVisibleVariables = None):
        super().__init__()
        self.__variables = variables or ['SDS_P1', 'SDS_P2']
        self.__alwaysVisibleVariables = alwaysVisibleVariables or ['lat', 'long']
        # diccionario {label : df}
        self.__datasets = {}
        self.__tabs = []
        self.__imputationMethods = imputationMethods

        self.__currentTab = None

    @property
    def variables(self):
        return self.__variables
    
    @property
    def alwaysVisibleVariables(self):
        return self.__variables

    @property
    def datasets(self):
        return self.__datasets
    
    def getDataset(self, label):
        return self.__datasets.get(label)
    
    @property
    def tabs(self):
        return self.__tabs
    
    @property
    def imputationMethods(self):
        return self.__imputationMethods
    
    @property
    def currentTab(self):
        return self.__currentTab
    
    def addDataset(self,label, df):
        """
        Add dataset to list
        
        Args:
            label (str): First number.
            df (pandas.DataFrame): Second number.
        """
        valid = True
        for var in self.__alwaysVisibleVariables:
            if var not in df.columns:
                valid = False
        if valid:
            safeName = self.tryName(label)
            self.__datasets.update({safeName : df})
            self.datasetAdded.emit(safeName)
        return

    def renameDataset(self, oldLabel, newLabel):
        """
        Validate and change dataset label.
        
        Args:
            oldLabel (str): Old name.
            newLabel (str): New Name

        Returns:
            bool: Success of the operation.
        """
        if newLabel and oldLabel != newLabel:
            df = self.__datasets.pop(oldLabel)
            if not df.empty:
                label = self.tryName(newLabel)
                self.__datasets.update({label : df})
                renamePairs = {oldLabel:label}
                self.renameDatasetsInTabs(oldLabel, label)
                self.datasetRenamed.emit(oldLabel, renamePairs)
                return True
        else:
            return False

    def renameDatasetsInTabs(self, oldLabel, newLabel):
        """Rename Dataset in visible in __tabs"""
        for tab in self.__tabs:
            tab.replaceVisible(oldLabel, newLabel)

    def convertCurrent(self):
        """Create dataset from current imputation results and add it to list."""
        current = self.__currentTab.results
        if current and self.__currentTab.getVisibleImputationVariables and self.__currentTab.type != 'Analysis':
            merged = pd.DataFrame()
            labelAddOns = []
            for key in self.__variables:
                value = current.get(key)
                imputationSelection = self.currentTab.getImputationSelection(key)
                if key in current.keys() and imputationSelection:
                    labelAddOns.append(key)
                    labelAddOns.append(imputationSelection)
                    merged = merged.combine_first(value)
            baseName = self.__currentTab.selection
            label = self.genName(baseName, labelAddOns)
            self.addDataset(label, merged)

    def removeDataset(self, label):
        """
        Dataset removal.

        Args:
            label (str): Label of the dataset to remove.

        Returns:
            bool: Success of removal.
        """
        if label in self.__datasets:
            columns = list(self.__datasets.pop(label).columns)            
            for tab in self.tabs:
                tab.clearIfWorking(label)
            self.datasetRemoved.emit(label, columns)
            return True
        else:
            return False

    def saveToCSV(self, labels, file):
        """
        Export __datasets as csv files.

        Args:
            labels (array<str>): Dataset list to export
            file (str): Filename
        """
        if len(labels) > 1:
            counter = 1
            for label in labels:
                name, ext = os.path.splitext(file)
                newFile = f"{name}({counter}){ext}"
                self.__datasets[label].to_csv(newFile, index=False, parse_dates = ["time"])
                counter+=1
        else:
            self.__datasets[label[0]].to_csv(file, index=False)
    
    def saveFuseToCSV(self, labels, file):
        """
        Export __datasets fused as one csv files.

        Args:
            labels (array<str>): Dataset list to export
            file (str): Filename
        """
        frames = []
        for label in labels:
            frames.append(self.__datasets[label])
        combined = pd.concat(frames)
        combined= combined.drop_duplicates()
        combined = combined.reset_index(drop=True)
        combined.to_csv(file,index=False)

    def loadFromCSV(self, file):
        """
        Import dataset from csv file.

        Args:
            file (str): File name.
        """
        frame = pd.read_csv(file)
        label = Path(file).stem
        self.addDataset(label, frame)

    def loadFuseFromCSVs(self, files):
        """
        Import dataset fusing multiple csv files.

        Args:
            files (array<str>): File names.
        """
        frames = []
        for file in files:
            frames.append(pd.read_csv(file))
        combined = pd.concat(frames)
        combined= combined.drop_duplicates()
        combined = combined.reset_index(drop=True)
        label = "Combined" + str(time.time())
        self.addDataset(label, combined)

    def impute(self, column):
        """
        Prepare current dataset and impute current based on current selection.

        Args:
            column (str): DataFrame column to impute.

        Returns:
            bool: Sucess of operation.
        """
        selection = self.__currentTab.selection
        imputationSelection = self.__currentTab.getImputationSelection(column)
        if imputationSelection and selection:
            imputationMetod = self.__imputationMethods.get(imputationSelection)
            if imputationMetod:
                try:
                    df = self.__datasets[selection]
                except:
                    return False
                if column in df.columns:
                    result = imputationMetod.impute(df, column,{'label': selection})
                else:
                    return False
                self.__currentTab.results.update({column:result})
                return True
            else: 
                return False
        else:
            return False

    def removePercent(self, label, value):
        """
        Remove a number of values from a dataframe equal 
        to a percentage of the total

        Args:
            label (str): Label of the DataFrame affected.
            value (int): Percentage of removal.
        """
        if label in self.__datasets:
            df = self.__datasets[label]
            result = removePercentage(df,value)
            labelAddOns = ['rmPercent']
            name = self.genName(label, labelAddOns)
            self.addDataset(name,result)
    
    def removeInterval(self, label, inverted, start, end):
        """
        Remove a number of values from a dataframe equal
        which are outside or inside a given range.

        Args:
            label (str): Label of the DataFrame affected.
            inverted (bool): True if values inside the range should be removed.
            start (pandas.Timestampt): Start of the interval.
            end (pandas.Timestampt): End of the interval.
        """
        if label in self.__datasets:
            df = self.__datasets[label]
            if inverted:
                result = removeOutsideInterval(df,start,end)
            else:
                result = removeInterval(df,start,end)
            labelAddOns = ['rmInterval']
            name = self.genName(label, labelAddOns)
            self.addDataset(name,result)
            
    
    def _clearWorking(self, var = None):
        """
        Clear imputation results.

        Args:
            var (str, optional): Variable to which the results are related. Defaults to None.
        """
        if not var:
            for var in self.__currentTab.results.keys():
                self.clearResult.emit(var)
            self.__currentTab.results.clear()
        else:
            if var in self.__currentTab.results.keys():
                self.clearResult.emit(var)


    def setCurrent(self, labelText):
        """
        Set working dataset.

        Args:
            labelText (str): Dataset label
        """
        if labelText and self.__currentTab.selection != labelText:
            self.__currentTab.selection = labelText
            self._clearWorking()
            if self.__currentTab.type == 'AnalysisTab':
                self.compare()
            else:
                for var in self.__variables:
                    if self.__currentTab.getImputationSelection(var):
                        if self.impute(var):
                            lat = self.__currentTab.results.get('lat')
                            long = self.__currentTab.results.get('long')
                            if lat is None:
                                self.impute('lat')
                                lat = self.__currentTab.results.get('lat')
                            if long is None:
                                self.impute('long')
                                long = self.__currentTab.results.get('long')
                            self.__currentTab.results[var]['lat'] = lat['lat']
                            self.__currentTab.results[var]['long'] = long['long']
            self.resultUpdated.emit()

    def changeImputationSelection(self, variable, selectedMethod):
        """
        Change imputation for a given variable.

        Args:
            variable (str): Variable name.
            selectedMethod (str): Imputation method label
        """
        
        if selectedMethod in self.__imputationMethods and variable in self.__variables:
            if self.__currentTab.changeImputationMethod(variable, selectedMethod):
                if self.__currentTab.selection and self.__currentTab.getImputationSelection(variable):
                    self._clearWorking(variable)
                    self.impute(variable)
                    if variable == 'lat' or variable == 'long':
                        coor = self.__currentTab.results.get(variable)
                        if coor:
                            for dsd in self.__variables:
                                if dsd in self.__currentTab.results:
                                    self.__currentTab.results[dsd][variable] = coor[variable]
                            self.resultUpdated.emit()
                    else:
                        self.imputationChanged.emit(variable)

    def changeImputationVisiblity(self, variable, checked):
        """
        Change imputation visibility of a variable for a given value.

        Args:
            variable (str): Variable name.
            checked (bool): New visibility value.
        """
        if variable in self.__variables:
            self.__currentTab.changeImputationVisibility(variable, checked)
            if self.__currentTab.selection and checked:
                self._clearWorking(variable)
                if self.impute(variable):
                    lat = self.__currentTab.results.get('lat')
                    long = self.__currentTab.results.get('long')
                    if not lat is None and not long is None:
                        for dsd in self.__variables:
                            if dsd in self.__currentTab.results:
                                self.__currentTab.results[dsd]['lat'] = lat['lat']
                                self.__currentTab.results[dsd]['long'] = long['long']
            self.imputationVisible.emit(variable, checked)

    def changeDatasetVisiblity(self, label, checked):
        """
        Change imputation visibility of a variable for a given value.

        Args:
            label (str): Dataset label.
            checked (str): New visibility status.
        """
        if label not in self.__currentTab.visible and checked:
            self.__currentTab.visible.append(label)
        elif label in self.__currentTab.visible and not checked:
            self.__currentTab.visible.remove(label)
        self.datasetVisilityChanged.emit(label, checked)

    def addTab(self, tabName, className, maxSelection = 1):
        """
        Adds tab to __tabs.

        Args:
            tabName (str): Tab title.
            className (str): Class name of the tab to add.
        """
        tab = TabInfo(className, self.__variables + self.__alwaysVisibleVariables, next(iter(self.__imputationMethods), None), 
                      title=tabName, maxSelection=maxSelection)
        for var in self.__alwaysVisibleVariables:
            tab.changeImputationVisibility(var, True)
        self.__tabs.append(tab)
        self.changeTab(len(self.__tabs)-1)
        return
    
    def removeTab(self, tabIndex):
        """
        Remove tab from __tabs and change current tab.

        Args:
            tabIndex (int): Tab index.
        """
        tab = self.__tabs.pop(tabIndex)
        if tab == self.__currentTab:
            if self.__tabs:
                self.__currentTab = self.__tabs[-1]
            else:
                self.__currentTab = None
        return

    def renameTab(self, index, newName):
        """
        Change tab title for new one.

        Args:
            index (int): Tab index.
            newName (str): New name.
        """
        self.__tabs[index].title = newName
        return

    def compare(self):
        """
        Update RMSE.

        Returns:
            bool: Success of operation.
        """
        selection = self.__currentTab.selection
        if selection and len(selection) > 1:
            predicted = self.__datasets[selection[0]]
            actual = self.__datasets[selection[1]]
            if not selection[0] == selection[1]:
                for var in self.__variables:
                    if var in predicted and var in actual:
                        rmse = self.rootMeanSquaredError(predicted, actual, var)
                        self.__currentTab.results.update({var: rmse})
                return True
        else:
            return False
    
    def rootMeanSquaredError(self, predicted, actual, col):
        """
        Calculate RMSE between __datasets.

        Args:
            predicted (pandas.DataFrame): Expeted DataFrame.
            actual (pandas.DataFrame): Actual DataFrame.
            col (str): Column to compare.

        Returns:
            float: RMSE value.
        """
        meanSquaredError = ((predicted[col] - actual[col]) ** 2).mean()
        rmse = np.sqrt(meanSquaredError)
        return rmse
        
    def changeTab(self, index):
        """
        Change current tab.

        Args:
            index (int): Tab index.
        """
        if index > len(self.__tabs) or index < 0:
            self.__currentTab = None
            self.currentTabChanged.emit(-1)
        elif len(self.__tabs) > 0:
            if not self.__currentTab == self.__tabs[index]:
                self.__currentTab = self.__tabs[index]
                self.currentTabChanged.emit(index)

    def duplicateDataset(self, label):
        """
        DuplicateDataset

        Args:
            label (str): Dataset label.
        """
        newLabel = self.genName(label, ["duplicate"])
        newDf = self.__datasets[label].copy()
        self.addDataset(newLabel, newDf)
    
    def applyCorrection(self, label, substract, division):
        """
        Apply correction values to dataset.

        Args:
            label (str): Dataset label.
            substract (float): Substract value.
            division (float): Dividend.
        """
        if label in self.__datasets:
            df = self.__datasets[label].copy()
            df[self.__variables[0]] = (df[self.__variables[0]] - substract) / division
            df[self.__variables[1]] = (df[self.__variables[1]] - substract) / division
            newLabel = self.genName(label, ["corrected"])
            self.addDataset(newLabel, df)

    def getResults(self):
        """
        Get all results.

        Returns:
            dict<str, pandas.DataFrame>: Current imputation results.
        """
        copy = self.__currentTab.results.copy()
        variables = self.__currentTab.results.keys()
        results = {}
        for val in variables:
            if val in self.__variables:
                results.update({val: copy[val]})

        return results
    
    def getVarResult(self, var):
        """
        Get result related to given variable.

        Args:
            var (str): Variable name.

        Returns:
            pandas.DataFrame: Current imputation results.
        """
        return self.__currentTab.results.get(var, None)

    def genName(self, base, addOns):
        """Generate new dataset label.

        Args:
            base (str): Base name.
            addOns (array<str>): Extra name suffixes.

        Returns:
            str: Generated name.
        """
        newName = base
        for var in addOns:
            newName += ('-' + var)
        return newName
    
    def tryName(self, name):
        """Test name against exising names and generate new one.

        Args:
            name (str): Candidate name for dataset.

        Returns:
            str: Valid dataset name.
        """
        checklist = list(self.__datasets.keys())
        checklist = checklist + self.__variables
        counter = 0
        newname = name
        while newname in checklist:
            counter += 1
            newname = name + '(' + str(counter) +')'
        return newname
