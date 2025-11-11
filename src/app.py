import os, sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

config_path = resource_path("config.ini")

from control.dataset_controller import DatasetControler
from model.dataset_list import DatasetList
from view.renamable_tab_widget import RenamableTabWidget
from view.impute_panel import ImputePanel
from view.dataset_panel import DatasetPanel
from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
from model.strategy.average import Average
from model.strategy.backward_fill import BackwardFill
from model.strategy.forward_fill import ForwardFill
from model.strategy.median import Median
from model.strategy.pypots_saits import PyPotsSaits
from model.strategy.pypots_transformer import PyPotsTransformer

def readyModel():
    if hasattr(sys, "_MEIPASS"):
        config_path = os.path.join(sys._MEIPASS, "config.ini")
    else:
        config_path = os.path.join(os.path.abspath("."), "config.ini")
    from model.dataset_list import DatasetList
    from model.strategy.average import Average
    from model.strategy.backward_fill import BackwardFill
    from model.strategy.forward_fill import ForwardFill
    from model.strategy.median import Median
    from model.strategy.pypots_saits import PyPotsSaits
    from model.strategy.pypots_transformer import PyPotsTransformer
    
    return

def createViewController():
    """
    Create view and controller

    Returns:
        MainWindow: View
        DatasetControler: Controller
    """
    from control.dataset_controller import DatasetControler
    from view.renamable_tab_widget import RenamableTabWidget
    from view.impute_panel import ImputePanel
    from view.dataset_panel import DatasetPanel
    from view.main_window import MainWindow
    methods = {
        'Average' : Average(), 
        'Backward Fill' : BackwardFill(), 
        'Forward Fill' : ForwardFill(), 
        'Median' : Median(),
        'PyPots SAITS' : PyPotsSaits(),
        'PyPots Transformer' : PyPotsTransformer()
    }
    model = DatasetList(methods)
    tabWidget = RenamableTabWidget()
    datPanel = DatasetPanel()
    impPanel = ImputePanel()
    view = MainWindow(tabWidget, [datPanel, impPanel])
    controller = DatasetControler(model, view, datPanel, impPanel, tabWidget)
    return view, controller

if __name__ == '__main__':
    """Main funtion to run app without launcher"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    methods = {
            'Average' : Average(), 
            'Backward Fill' : BackwardFill(), 
            'Forward Fill' : ForwardFill(), 
            'Median' : Median(),
            'PyPots SAITS' : PyPotsSaits(),
            'PyPots Transformer' : PyPotsTransformer()
        }
    model = DatasetList(methods)
    tabWidget = RenamableTabWidget()
    datPanel = DatasetPanel()
    impPanel = ImputePanel()
    view = MainWindow(tabWidget, [datPanel, impPanel])
    controller = DatasetControler(model, view, datPanel, impPanel, tabWidget)
    
    
    view.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')