from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QDialog
from PyQt5.QtGui import QDoubleValidator

class CorrectionDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Correction Inputs")
        self.resize(400, 150)
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Real Value = (Measured Value - x) / y"))

        self.__substractInput = QLineEdit()
        self.__substractInput.setValidator(QDoubleValidator())
        self.layout.addWidget(QLabel("Substract (x) : "))
        self.layout.addWidget(self.__substractInput)

        self.__divisionInput = QLineEdit()
        self.__divisionInput.setValidator(QDoubleValidator())
        self.layout.addWidget(QLabel("Divide by (y) : "))
        self.layout.addWidget(self.__divisionInput)

        okButton = QPushButton("Apply")
        okButton.clicked.connect(self.accept)
        self.layout.addWidget(okButton)

        self.setLayout(self.layout)

    def getOperands(self):
        if not self.__substractInput.text().strip() or not self.__divisionInput.text().strip():
            return None, None
        substract = float(self.__substractInput.text())
        division = float(self.__divisionInput.text())
        return substract, division