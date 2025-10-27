from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QLabel, QRadioButton, QDialogButtonBox

class ImportDialog(QDialog):

    def __init__(self, selectedFiles):
        super().__init__()

        self.setWindowTitle("Import Dialog")
        layout = QVBoxLayout()
        self.resize(500, 200)

        # Etiqueta
        layout.addWidget(QLabel("Items:"))

        # List widget
        selectionList = QListWidget()
        selectionList.addItems(selectedFiles)
        layout.addWidget(selectionList)

        # Botones de selección
        
        self.fuseOption = QRadioButton("Fuse as one dataset")
        self.multipleOption = QRadioButton("Import as multiple datasets")
        self.multipleOption.setChecked(True)  # Default checked

        layout.addWidget(self.fuseOption)
        layout.addWidget(self.multipleOption)
        
        # OK Button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)
        
    def getSelection(self):
        return {
            "fuse": self.fuseOption.isChecked(),
            "multiple": self.multipleOption.isChecked()
        }