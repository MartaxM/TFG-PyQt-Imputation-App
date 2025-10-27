from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSizePolicy, QAction, QVBoxLayout, QStyle
from PyQt5.QtCore import pyqtSignal, Qt

class MainWindow(QMainWindow):

    openImportDialog = pyqtSignal()
    openExportDialog = pyqtSignal()
    addTabSignal = pyqtSignal(str)

    def __init__(self, mainWidget, menuSections):
        super().__init__()

        # Set up de la ventana
        self.setWindowTitle('PyQt Imputation App')
        self.window_width, self.window_height = 800, 600
        self.setMinimumSize(self.window_width, self.window_height)
        self.setStyleSheet('''
            QWidget {
                font-size: 14px;
            }
        ''')
        icon = self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.setWindowIcon(icon)
        
        # Preparar paneles
        centralWidget = QWidget()
        mainLayout = QHBoxLayout()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        sideMenu = QWidget()
        sideMenu.setFixedWidth(400)
        sideMenu.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sideMenuLayout = QVBoxLayout(sideMenu)
        sideMenuLayout.setAlignment(Qt.AlignTop)

        # Añadir paneles
        for panel in menuSections:
            sideMenuLayout.addWidget(panel)
        # Añadir a layout
        mainLayout.addWidget(mainWidget)
        mainLayout.addWidget(sideMenu)
        
        # Crear superior menu bar
        menu = self.menuBar()
        fileMenu = menu.addMenu("&File")
        viewMenu = menu.addMenu("&Add View")

        # Crear acciones de los menus
        # Acciones Files
        importAction = QAction("&Import from file", self)
        importAction.triggered.connect(self.openImportDialog)
        exportAction = QAction("&Export to file", self)
        exportAction.triggered.connect(self.openExportDialog)

        # Acciones View
        addMapAction = QAction("&Map Tab", self)
        addMapAction.triggered.connect(self.addMapTab)
        addPlotAction = QAction("&Plot Tab", self)
        addPlotAction.triggered.connect(self.addPlotTab)
        addAnalysisAction = QAction("&Analysis Tab", self)
        addAnalysisAction.triggered.connect(self.addAnalysisTab)
        
        # Añadir opciones a los menus
        fileMenu.addAction(importAction)
        fileMenu.addAction(exportAction)

        viewMenu.addAction(addMapAction)
        viewMenu.addAction(addPlotAction)
        viewMenu.addAction(addAnalysisAction)
        
    def addMapTab(self):
        self.addTabSignal.emit("Map")

    def addPlotTab(self):
        self.addTabSignal.emit("Plot")
    
    def addAnalysisTab(self):
        self.addTabSignal.emit("Analysis")