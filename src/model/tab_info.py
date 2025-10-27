class TabInfo():
    
    def __init__(self, type, title = "", visible = []
                 , selection = [], results={}, maxSelection = 1):
        #
            # { label: label
            # visible: visible
            # current: current dataset
            # results: working datasets
            # class: tabType}
        #
        self.title = title
        self.visible = visible
        self.results = results
        self.__selection = selection
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
            None
    
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