from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import QDoubleValidator

class CorrectionDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Correction Inputs")
        self.resize(400, 150)
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Real Value = (Measured Value - x) / y"))

        self.substractInput = QLineEdit()
        self.substractInput.setValidator(QDoubleValidator())
        self.layout.addWidget(QLabel("Substract (x) : "))
        self.layout.addWidget(self.substractInput)

        self.divisionInput = QLineEdit()
        self.divisionInput.setValidator(QDoubleValidator())
        self.layout.addWidget(QLabel("Divide by (y) : "))
        self.layout.addWidget(self.divisionInput)

        okButton = QPushButton("Apply")
        okButton.clicked.connect(self.accept)
        self.layout.addWidget(okButton)

        self.setLayout(self.layout)

    def getOperands(self):
        if not self.substractInput.text().strip() or not self.divisionInput.text().strip():
            return None, None
        substract = float(self.substractInput.text())
        division = float(self.divisionInput.text())
        return substract, division