from PyQt5.QtWidgets import QLabel, QGroupBox, QVBoxLayout
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from view.tab_widget_base import TabWidgetBase

class AnalysisTab(TabWidgetBase):
    def __init__(self, parent=None):
        super().__init__()
        self.title = QLabel("Comparison")
        self.labels={}
        # GroupBox SDS_P1
        self.groupSDS_P1 = QGroupBox("SDS_P1")
        self.labels['SDS_P1'] = {"RSME" : QLabel("No value")}
        group1Layout = QVBoxLayout()
        for label in self.labels['SDS_P1'].values():
            group1Layout.addWidget(label)
        self.groupSDS_P1.setLayout(group1Layout)

        # GroupBox SDS_P2
        self.groupSDS_P2 = QGroupBox("SDS_P2")
        self.labels['SDS_P2'] = {"RSME" : QLabel("No value")}
        group2Layout = QVBoxLayout()
        for label in self.labels['SDS_P2'].values():
            group2Layout.addWidget(label)
        self.groupSDS_P2.setLayout(group2Layout)

        # Missing data message
        self.missing_label = QLabel("⚠️ Missing or invalid data")
        self.missing_label.setStyleSheet("color: red; font-weight: bold;")
        self.missing_label.setVisible(False)

        # Main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.title)
        mainLayout.addWidget(self.groupSDS_P1)
        mainLayout.addWidget(self.groupSDS_P2)
        mainLayout.addWidget(self.missing_label)
        mainLayout.setAlignment(Qt.AlignTop)
        self.setLayout(mainLayout)

    def show_missing_data_message(self):
        self.groupSDS_P1.hide()
        self.groupSDS_P2.hide()
        self.missing_label.setVisible(True)

    def show_groups(self):
        self.groupSDS_P1.show()
        self.groupSDS_P2.show()
        self.missing_label.setVisible(False)

    def addLayer(self, label, df, column):
        return

    def removeLayer(self, label, column = None):
        return
    
    def reload(self, df_list, column = None):
        pass

    def updateViewResult(self, results):
        for key, result in results.items():
            self.labels[key]["RSME"].setText(f"RMSE: {str(result)}")