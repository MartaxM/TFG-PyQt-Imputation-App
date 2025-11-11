from PyQt5.QtWidgets import QDialog, QListWidget, QStackedWidget, QHBoxLayout, QWidget, QVBoxLayout, QPushButton, QLineEdit,QDateTimeEdit, QCheckBox,QLabel
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QDateTime, Qt
import pandas as pd

class RemoveDialog(QDialog):
    def __init__(self, df, datetimeCol = "time"):
        super().__init__()
        self.setWindowTitle("Options Dialog")
        self.resize(400, 300)

        self.__selection = {}

        self.__listWidget = QListWidget()
        self.__listWidget.setFixedWidth(150)
        self.__listWidget.addItems(["Random Percent", "Interval"])
        self.__listWidget.itemSelectionChanged.connect(self.__onSelectionChanged)

        stack = QStackedWidget()
        stack.addWidget(self.__randomWidget())
        stack.addWidget(self.__intervalWidget(df, datetimeCol))

        layout = QHBoxLayout()
        layout.addWidget(self.__listWidget)
        layout.addWidget(stack)
        self.setLayout(layout)

        self.__listWidget.currentRowChanged.connect(stack.setCurrentIndex)
        self.__listWidget.setCurrentRow(0)  # Select first by default

        
    def __onSelectionChanged(self):
        selectedIndexes = self.__listWidget.selectedIndexes()
        if selectedIndexes:
            index = selectedIndexes[0].row()  # get row index of first selected item
            if index == 0:
                self.__selection.update({'mode': 'percent'})
            elif index == 1:
                self.__selection.update({'mode': 'interval'})
            elif index == 1:
                self.__selection.update({'mode': 'values'})
        else:
            self.__selection['mode'] = 'undefined'

    def __randomWidget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        removeBtn = QPushButton("Remove data", self)
        removeBtn.clicked.connect(self.savePercentRemoveInput)
        self.__removePercentageInput = QLineEdit()
        intValidator = QIntValidator()
        intValidator.setRange(1,99)
        self.__removePercentageInput.setValidator(intValidator)
        self.__removePercentageInput.setPlaceholderText("Percent 1-99")
        layout.addWidget(self.__removePercentageInput)
        layout.addStretch()
        layout.addWidget(removeBtn, alignment=Qt.AlignRight)
    
        widget.setLayout(layout)
        return widget

    def __intervalWidget(self, df, datetimeCol):
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
        self.__startDatetime = QDateTimeEdit(self)
        self.__startDatetime.setCalendarPopup(True)
        self.__startDatetime.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.__startDatetime.setDateTime(startQdt)

        # Ending date/time
        self.__endDatetime = QDateTimeEdit(self)
        self.__endDatetime.setCalendarPopup(True)
        self.__endDatetime.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.__endDatetime.setDateTime(endQdt)

        self.__invertedCheckbox = QCheckBox("Values inside the selection will be kept", self)
        self.__invertedCheckbox.setChecked(True)

        layout.addWidget(self.__startDatetime)
        layout.addWidget(self.__endDatetime)
        layout.addWidget(self.__invertedCheckbox)
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
        rp = self.__removePercentageInput.text()
        if not rp:
            self.reject()
        else:
            self.__selection.update({'mode': 'percent'})
            self.__selection.update({'value':  int(rp)/100})
            self.accept()

    def saveIntervalRemoveInput(self):
        startDatetime = self.__startDatetime.dateTime().toPyDateTime()
        endDatetime = self.__endDatetime.dateTime().toPyDateTime()
        startTimestamp = pd.Timestamp(startDatetime)
        endTimestamp = pd.Timestamp(endDatetime)
        inverted = self.__invertedCheckbox.isChecked()
        
        if not startTimestamp or not endTimestamp:
            self.reject()
        else:
            self.__selection.update({'mode': 'interval'})
            self.__selection.update({'inverted': inverted})
            self.__selection.update({'start': startTimestamp})
            self.__selection.update({'end': endTimestamp})
            self.accept()

    def getSelection(self):
        return self.__selection