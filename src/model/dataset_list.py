from PyQt5.QtCore import QObject, pyqtSignal
import pandas as pd
import time
import os
from pathlib import Path
from model.strategy.average import Average
from model.strategy.backward_fill import BackwardFill
from model.strategy.forward_fill import ForwardFill
from model.strategy.median import Median
from model.strategy.pypots_saits import PyPotsSaits
from model.strategy.pypots_transformer import PyPotsTransformer
from model.tab_info import TabInfo
from model.remove import *

class DatasetList(QObject):
    datasetChanged = pyqtSignal(str)
    datasetAdded = pyqtSignal(str)
    datasetAddedToVisible = pyqtSignal(str)
    datasetRemoved = pyqtSignal(str)
    datasetRenamed = pyqtSignal(str, dict)
    currentTabChanged = pyqtSignal(int)
    resultUpdated = pyqtSignal()
    imputationChanged = pyqtSignal(str)
    imputationVisible = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.variables = ['SDS_P1', 'SDS_P2']
        # diccionario {label : df}
        self.datasets = {}
        self.tabs = []
        self.imputationMethods =  {
            'Average' : Average(), 
            'Backward Fill' : BackwardFill(), 
            'Forward Fill' : ForwardFill(), 
            'Median' : Median(),
            'PyPots SAITS' : PyPotsSaits(),
            'PyPots Transformer' : PyPotsTransformer()
        }
        self.imputationSelection = {
            self.variables[0] : {
                'visible': False,
                'selection':'Average'
            },
            self.variables[1] : {
                'visible': False,
                'selection':'Average'
            },
            'lat' : {
                'visible': True,
                'selection':'Average'
            },
            'long' : {
                'visible': True,
                'selection':'Average'
            }
        }
        self.currentTab = None

    def addDataset(self,label, df):
        """
        Add dataset to list
        
        Args:
            label (str): First number.
            df (pandas.DataFrame): Second number.
        """
        safeName = self.tryName(label)
        self.datasets.update({safeName : df})
        self.datasetAdded.emit(safeName)

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
            df = self.datasets.pop(oldLabel)
            if not df.empty:
                label = self.tryName(newLabel)
                self.datasets.update({label : df})
                renamePairs = {oldLabel:label}
                self.renameDatasetsInTabs()
                self.datasetRenamed.emit(oldLabel, renamePairs)
                return True
        else:
            return False

    def renameDatasetsInTabs(self):
        """Rename Dataset in visible in tabs"""
        pass
        

    def convertCurrent(self):
        """Create dataset from current imputation results and add it to list."""
        current = self.currentTab.results
        if current and self.currentTab.type != 'Analysis':
            merged = pd.DataFrame()
            labelAddOns = []
            for key in self.variables:
                value = current.get(key)
                if key in current.keys() and self.imputationSelection[key]['visible']:
                    labelAddOns.append(key)
                    labelAddOns.append(self.imputationSelection[key]['selection'])
                    merged = merged.combine_first(value)
            baseName = self.currentTab.selection
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
        if label in self.datasets:
            self.datasets.pop(label)
            self.datasetRemoved.emit(label)
            if label == self.currentTab.selection:
                self._clearWorking()
            return True
        else:
            return False

    def saveToCSV(self, labels, file):
        """
        Export datasets as csv files.

        Args:
            labels (array<str>): Dataset list to export
            file (str): Filename
        """
        if len(labels) > 1:
            counter = 1
            for label in labels:
                name, ext = os.path.splitext(file)
                newFile = f"{name}({counter}){ext}"
                self.datasets[label].to_csv(newFile, index=False, parse_dates = ["time"])
                counter+=1
        else:
            self.datasets[label[0]].to_csv(file, index=False)
    
    def saveFuseToCSV(self, labels, file):
        """
        Export datasets fused as one csv files.

        Args:
            labels (array<str>): Dataset list to export
            file (str): Filename
        """
        frames = []
        for label in labels:
            frames.append(self.datasets[label])
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
        frame['imputated'] = False
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
        combined['imputated'] = False
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
        if column in self.variables and self.currentTab.selection:
            imputationMetod = self.imputationMethods.get(self.imputationSelection[column]['selection'])
            if imputationMetod:
                df = self.datasets[self.currentTab.selection]
                fullIndex = range( 0, df.index.max() + 1)
                df = df.reindex(fullIndex)
                result = imputationMetod.impute(df, column)
                self.currentTab.results.update({column:result})
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
        if label in self.datasets:
            df = self.datasets[label]
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
        if label in self.datasets:
            df = self.datasets[label]
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
            for var in self.currentTab.results.keys():
                self.datasetRemoved.emit(var)
            self.currentTab.results.clear()
        else:
            if var in self.currentTab.results.keys():
                self.datasetRemoved.emit(var)


    def setCurrent(self, labelText):
        """
        Set working dataset.

        Args:
            labelText (str): Dataset label
        """
        if self.currentTab.selection != labelText:
            self.currentTab.addSelection(labelText)
            self._clearWorking()
            if self.currentTab.type == 'AnalysisTab':
                self.compare()
            else:
                for var, obj in self.imputationSelection.items():
                    if obj['visible']:
                        self.impute(var)
                results = self.currentTab.results
                lat = results.get('lat')
                long = results.get('long')
                if lat and long:
                    for var, obj in self.imputationSelection.items():
                        if obj['visible']:
                            for dsd in self.variables:
                                if dsd in results:
                                    self.currentTab.results[dsd]['lat'] = lat['lat']
                                    self.currentTab.results[dsd]['long'] = long['long']
            self.resultUpdated.emit()

    def changeImputationSelection(self, variable, selectedMethod):
        """
        Change imputation for a given variable.

        Args:
            variable (str): Variable name.
            selectedMethod (str): Imputation method label
        """
        if selectedMethod in self.imputationMethods and variable in self.variables:
            if self.imputationSelection[variable]['selection'] != selectedMethod:
                self.imputationSelection[variable].update({'selection':selectedMethod})
                if self.currentTab.selection and self.imputationSelection[variable]['visible']:
                    self._clearWorking(variable)
                    self.impute(variable)
                    if variable == 'lat' or variable == 'long':
                        coor = self.currentTab.results.get(variable)
                        if coor:
                            for dsd in self.variables:
                                if dsd in self.currentTab.results:
                                    self.currentTab.results[dsd][variable] = coor['df'][variable]
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
        if variable in self.imputationSelection:
            self.imputationSelection[variable].update({'visible':checked})
            if self.currentTab.selection and checked:
                self._clearWorking(variable)
                self.impute(variable)
                lat = self.currentTab.results.get('lat')
                long = self.currentTab.results.get('long')
                if lat and long:
                    for dsd in self.variables:
                        if dsd in self.currentTab.results:
                            self.currentTab.results[dsd]['df']['lat'] = lat['df']['lat']
                            self.currentTab.results[dsd]['df']['long'] = long['df']['long']
            self.imputationVisible.emit(variable, checked)

    def changeDatasetVisiblity(self, label, checked):
        """
        Change imputation visibility of a variable for a given value.

        Args:
            label (str): Dataset label.
            checked (str): New visibility status.
        """
        if label not in self.currentTab.visible and checked:
            self.currentTab.visible.append(label)
            self.datasetAddedToVisible.emit(label)
        elif label in self.currentTab.visible and not checked:
            self.currentTab.visible.remove(label)
            self.datasetRemoved.emit(label)

    def addTab(self, tabName, className, maxSelection = 1):
        """
        Adds tab to tabs.

        Args:
            tabName (str): Tab title.
            className (str): Class name of the tab to add.
        """
        tab = TabInfo(className, title=tabName, maxSelection=maxSelection)
        self.tabs.append(tab)
        self.changeTab(len(self.tabs)-1)
        return
    
    def removeTab(self, tabIndex):
        """
        Remove tab from tabs and change current tab.

        Args:
            tabIndex (int): Tab index.
        """
        tab = self.tabs.pop(tabIndex)
        if tab == self.currentTab:
            if self.tabs:
                self.currentTab = self.tabs[-1]
            else:
                self.currentTab = None
        return

    def renameTab(self, index, newName):
        """
        Change tab title for new one.

        Args:
            index (int): Tab index.
            newName (str): New name.
        """
        self.tabs[index]['label'] = newName
        return

    def compare(self):
        """
        Update RMSE.

        Returns:
            bool: Success of operation.
        """
        selection = self.currentTab.selection
        if selection:
            predicted = self.datasets[selection[0]]
            actual = self.datasets[selection[1]]
            if selection[0] != selection[1]:
                for var in self.variables:
                    if var in predicted and var in actual:
                        rmse = self.rootMeanSquaredError(predicted, actual, var)
                        self.currentTab.results.update({var: rmse})
                return True
        else:
            return False
    
    def rootMeanSquaredError(self, predicted, actual, col):
        """
        Calculate RMSE between datasets.

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
        if index > len(self.tabs) or index < 0:
            self.currentTab = None
        else:
            self.currentTab = self.tabs[index]
            self.currentTabChanged.emit(index)

    def duplicateDataset(self, label):
        """
        DuplicateDataset

        Args:
            label (str): Dataset label.
        """
        newLabel = self.genName(label, ["duplicate"])
        newDf = self.datasets[label].copy()
        self.addDataset(newLabel, newDf)
    
    def applyCorrection(self, label, substract, division):
        """
        Apply correction values to dataset.

        Args:
            label (str): Dataset label.
            substract (float): Substract value.
            division (float): Dividend.
        """
        if label in self.datasets:
            df = self.datasets[label].copy()
            df[self.variables[0]] = (df[self.variables[0]] - substract) / division
            df[self.variables[1]] = (df[self.variables[1]] - substract) / division
            newLabel = self.genName(label, ["corrected"])
            self.addDataset(newLabel, df)

    def getResults(self):
        """
        Get all results.

        Returns:
            dict<str, pandas.DataFrame>: Current imputation results.
        """
        return self.currentTab.results.copy()
    
    def getVarResult(self, var):
        """
        Get result related to given variable.

        Args:
            var (str): Variable name.

        Returns:
            pandas.DataFrame: Current imputation results.
        """
        return self.currentTab.results[var]

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
        checklist = list(self.datasets.keys())
        checklist = checklist + self.variables
        counter = 0
        newname = name
        while newname in checklist:
            counter += 1
            newname = name + '(' + str(counter) +')'
        return newname
