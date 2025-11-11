from PyQt5.QtWidgets import QLabel, QGroupBox, QVBoxLayout
from PyQt5.QtCore import Qt
from view.tab_widget_base import TabWidgetBase

class AnalysisTab(TabWidgetBase):
    def __init__(self, parent=None):
        super().__init__()
        self.__title = QLabel("Comparison")
        self.__labels={}
        self.__groups = []

        # GroupBox SDS_P1
        groupSDS_P1 = QGroupBox("SDS_P1")
        self.__labels['SDS_P1'] = {"RSME" : QLabel("No value")}
        group1Layout = QVBoxLayout()
        for label in self.__labels['SDS_P1'].values():
            group1Layout.addWidget(label)
        groupSDS_P1.setLayout(group1Layout)
        self.__groups.append(groupSDS_P1)

        # GroupBox SDS_P2
        groupSDS_P2 = QGroupBox("SDS_P2")
        self.__labels['SDS_P2'] = {"RSME" : QLabel("No value")}
        group2Layout = QVBoxLayout()
        for label in self.__labels['SDS_P2'].values():
            group2Layout.addWidget(label)
        groupSDS_P2.setLayout(group2Layout)
        self.__groups.append(groupSDS_P2)

        # Missing data message
        self.__missing_label = QLabel("⚠️ Missing or invalid data")
        self.__missing_label.setStyleSheet("color: red; font-weight: bold;")
        self.__missing_label.setVisible(False)

        # Main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.__title)
        for group in self.__groups:
            mainLayout.addWidget(group)
        mainLayout.addWidget(self.__missing_label)
        mainLayout.setAlignment(Qt.AlignTop)
        self.setLayout(mainLayout)

    def showMissingDataMessage(self):
        for group in self.__groups:
            group.hide()
        self.__missing_label.setVisible(True)

    def showGroups(self):
        for group in self.__groups:
            group.show()
        self.__missing_label.setVisible(False)

    def addLayer(self, label, df, column):
        return

    def removeLayer(self, label, column = None):
        return
    
    def reload(self, df_list, column = None):
        pass

    def updateViewResult(self, results):
        for key, obj in self.__labels.items():
            if key in results:
                obj['RSME'].setText(str(results[key]))
            else:
                obj['RSME'].setText("No value")