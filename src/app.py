from control.dataset_controller import DatasetControler
from model.dataset_list import DatasetList
from view.renamable_tab_widget import RenamableTabWidget
from view.impute_panel import ImputePanel
from view.dataset_panel import DatasetPanel
from PyQt5.QtWidgets import QApplication
import sys
from view.main_window import MainWindow

if __name__ == '__main__':
    # Estrategias de imputación que queremos incluir
    
    # impStratLabels = []
    # for strat in imputeStrategies:
    #     impStratLabels.append(strat.getLabel())

    # # Estrategias de imputación para coordenadas que queremos incluir
    # imputeCoorStrategies = [Average(), BackwardFill(), ForwardFill(), Median()]
    # impCoorStratLabels = []
    # for strat in imputeCoorStrategies:
    #     impCoorStratLabels.append(strat.getLabel())

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    model = DatasetList()
    tabWidget = RenamableTabWidget()
    datPanel = DatasetPanel()
    impPanel = ImputePanel()
    view = MainWindow(tabWidget, [datPanel, impPanel])
    controller = DatasetControler(model, view, datPanel, impPanel, tabWidget)
    #controller = Controller(view, imputeStrategies, imputeCoorStrategies)
    #controller.run()
    view.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')