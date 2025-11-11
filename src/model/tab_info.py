class TabInfo():
    
    def __init__(self, type, variables, startingMethod , title = "",visible = None
                 , selection = None, results = None, maxSelection = 1, startingVisibility = False):
        
        self.title = title
        self.visible = visible or []
        self.results = results or {}
        self.__imputationSelection = {}
        for var in variables:
            self.__imputationSelection.update(
                {
                    var : {
                        'visible': startingVisibility,
                        'selection': startingMethod
                    }   
                }
            )
        self.__selection = selection or []
        self.__type = type
        self.__maxSelection = maxSelection
    
    @property
    def type(self):
        return self.__type
    
    @property
    def selection(self):
        if self.__maxSelection == len(self.__selection):
            if self.__maxSelection == 1:
                return self.__selection[0]
            else:
                return self.__selection
        else:
            return None
    
    @selection.setter
    def selection(self, selection):
        self.__selection.clear()
        if isinstance(selection, list):
            for val in selection:
                self.__selection.append(val)
        elif isinstance(selection, str):
            self.__selection.append(selection)
    
    def getVisibleImputationVariables(self):
        visibleImputation = []
        for var, status in self.__imputationSelection.items():
            if status['visible']:
                visibleImputation.append(var)

        return visibleImputation

    def getImputationSelection(self, var):
        impSelection = self.__imputationSelection.get(var)
        if impSelection and impSelection['visible']:
            return impSelection['selection']
        else:
            return None
        
    def changeImputationVisibility(self, var, visible):
        impSelection = self.__imputationSelection.get(var)
        if impSelection and not impSelection['visible'] == visible:
            impSelection['visible'] = visible
            return True
        else: 
            return False

    def changeImputationMethod(self, var, method):
        impSelection = self.__imputationSelection.get(var)
        if impSelection and not impSelection['selection'] == method:
            impSelection['selection'] = method
            return True
        else: 
            return False

    def addSelection(self, label):
        self.__selection.append(label)
        if len(self.__selection) > self.__maxSelection:
            del self.__selection[0]

    def removeSelection(self, label):
        self.__selection.remove(label)

    def changeVisibility(self, label, visible):
        if visible:
            if not label in self.visible:
                self.visible.append(label)
        else:
            self.remove(label)

    def replaceVisible(self, oldName, newName):
        try:
            index = self.visible.index(oldName)
        except:
            index = -1
        if index > -1:
            self.visible[index] = newName

    def clearIfWorking(self, label):
        if label in self.__selection:
            self.__selection.remove(label)
            if label in self.visible:
                self.visible.remove(label)
            for imputationSelection in self.__imputationSelection.values():
                imputationSelection['visible'] = False

            self.results.clear()
