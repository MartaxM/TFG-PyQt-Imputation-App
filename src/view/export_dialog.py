from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QGroupBox, QRadioButton, QDialogButtonBox
)


class ExportDialog(QDialog):
    def __init__(self, datasets):
        super().__init__()
        self.setWindowTitle("Select Items and Option")
        self.resize(500, 200)
        # Main layout
        main_layout = QVBoxLayout()

        # GroupBox with multi-select list
        group_box = QGroupBox("Select Items")
        group_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)

        for label in datasets:
            item = QListWidgetItem(label)
            self.list_widget.addItem(item)

        group_layout.addWidget(self.list_widget)
        group_box.setLayout(group_layout)
        main_layout.addWidget(group_box)

        # Radio buttons
        self.oneFileOptionOption = QRadioButton("Export as one file")
        self.multipleFilesOption = QRadioButton("Export as multiple files")
        self.multipleFilesOption.setChecked(True)  # Default selection
        main_layout.addWidget(self.oneFileOptionOption)
        main_layout.addWidget(self.multipleFilesOption)

        # OK button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(button_box)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def getSelection(self):
        selected_items = [
            item.text() for item in self.list_widget.selectedItems()
        ]
        selected_option = "One" if self.oneFileOptionOption.isChecked() else "Multiple"
        return selected_items, selected_option
