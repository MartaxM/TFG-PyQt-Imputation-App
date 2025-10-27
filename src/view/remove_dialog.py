from PyQt5.QtWidgets import QDialog, QListWidget, QStackedWidget, QHBoxLayout, QWidget, QVBoxLayout, QPushButton, QLineEdit,QDateTimeEdit, QCheckBox,QLabel
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QDateTime, Qt
import pandas as pd

class RemoveDialog(QDialog):
    def __init__(self, df, datetimeCol = "time"):
        super().__init__()
        self.setWindowTitle("Options Dialog")
        self.resize(400, 300)

        self.selection = {}

        self.listWidget = QListWidget()
        self.listWidget.setFixedWidth(150)
        self.listWidget.addItems(["Random Percent", "Interval"])
        self.listWidget.itemSelectionChanged.connect(self.onSelectionChanged)

        stack = QStackedWidget()
        stack.addWidget(self.randomWidget())
        stack.addWidget(self.intervalWidget(df, datetimeCol))

        layout = QHBoxLayout()
        layout.addWidget(self.listWidget)
        layout.addWidget(stack)
        self.setLayout(layout)

        self.listWidget.currentRowChanged.connect(stack.setCurrentIndex)
        self.listWidget.setCurrentRow(0)  # Select first by default

        
    def onSelectionChanged(self):
        selectedIndexes = self.listWidget.selectedIndexes()
        if selectedIndexes:
            index = selectedIndexes[0].row()  # get row index of first selected item
            if index == 0:
                self.selection.update({'mode': 'percent'})
            elif index == 1:
                self.selection.update({'mode': 'interval'})
            elif index == 1:
                self.selection.update({'mode': 'values'})
        else:
            self.selection['mode'] = 'undefined'

    def randomWidget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        removeBtn = QPushButton("Remove data", self)
        removeBtn.clicked.connect(self.savePercentRemoveInput)
        self.removePercentageInput = QLineEdit()
        intValidator = QIntValidator()
        intValidator.setRange(1,99)
        self.removePercentageInput.setValidator(intValidator)
        self.removePercentageInput.setPlaceholderText("Percent 1-99")
        layout.addWidget(self.removePercentageInput)
        layout.addStretch()
        layout.addWidget(removeBtn, alignment=Qt.AlignRight)
    
        widget.setLayout(layout)
        return widget

    def intervalWidget(self, df, datetimeCol):
        widget = QWidget()
        layout = QVBoxLayout()
        removeBtn = QPushButton("Remove data", self)
        removeBtn.clicked.connect(self.saveIntervalRemoveInput)

        df[datetimeCol] = pd.to_datetime(df[datetimeCol])
        firstTs = df[datetimeCol].min()
        lastTs = df[datetimeCol].max()

        # Convert pandas Timestamp to QDateTime (no ms)
        startQdt = QDateTime(firstTs.year, firstTs.month, firstTs.day,
                              firstTs.hour, firstTs.minute, firstTs.second)
        endQdt = QDateTime(lastTs.year, lastTs.month, lastTs.day,
                            lastTs.hour, lastTs.minute, lastTs.second)
        # Starting date/time
        self.startDatetime = QDateTimeEdit(self)
        self.startDatetime.setCalendarPopup(True)
        self.startDatetime.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.startDatetime.setDateTime(startQdt)

        # Ending date/time
        self.endDatetime = QDateTimeEdit(self)
        self.endDatetime.setCalendarPopup(True)
        self.endDatetime.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.endDatetime.setDateTime(endQdt)

        self.invertedCheckbox = QCheckBox("Values inside the selection will be kept", self)
        self.invertedCheckbox.setChecked(True)

        layout.addWidget(self.startDatetime)
        layout.addWidget(self.endDatetime)
        layout.addWidget(self.invertedCheckbox)
        layout.addStretch()
        layout.addWidget(removeBtn, alignment=Qt.AlignRight)
    
        widget.setLayout(layout)
        return widget

    def valuesWidget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Remove values here"))
        widget.setLayout(layout)
        return widget
    
    def savePercentRemoveInput(self):
        rp = self.removePercentageInput.text()
        if not rp:
            self.reject()
        else:
            self.selection.update({'mode': 'percent'})
            self.selection.update({'value':  int(rp)/100})
            self.accept()

    def saveIntervalRemoveInput(self):
        startDatetime = self.startDatetime.dateTime().toPyDateTime()
        endDatetime = self.endDatetime.dateTime().toPyDateTime()
        startTimestamp = pd.Timestamp(startDatetime)
        endTimestamp = pd.Timestamp(endDatetime)
        inverted = self.invertedCheckbox.isChecked()
        
        if not startTimestamp or not endTimestamp:
            self.reject()
        else:
            self.selection.update({'mode': 'interval'})
            self.selection.update({'inverted': inverted})
            self.selection.update({'start': startTimestamp})
            self.selection.update({'end': endTimestamp})
            self.accept()

    def getSelection(self):
        return self.selection