import pytest
from PyQt5.QtWidgets import QFileDialog, QDialog, QApplication
from src.model.dataset_list import DatasetList
from src.view.main_window import MainWindow
from src.view.renamable_tab_widget import RenamableTabWidget
from src.view.dataset_panel import DatasetPanel
from src.view.impute_panel import ImputePanel
from src.control.dataset_controller import DatasetControler

import sys

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

@pytest.fixture
def full_controller(qtbot):
    """Creates the real MVC setup."""
    model = DatasetList()
    ds_panel = DatasetPanel()
    im_panel = ImputePanel()
    tab_widget = RenamableTabWidget()
    view = MainWindow(tab_widget, [ds_panel, im_panel])
    

    ctrl = DatasetControler(model, view, ds_panel, im_panel, tab_widget)

    # add to qtbot for cleanup
    qtbot.addWidget(view)
    qtbot.addWidget(ds_panel)
    qtbot.addWidget(im_panel)
    qtbot.addWidget(tab_widget)

    return ctrl, model, view, ds_panel, im_panel, tab_widget


# --------------------------------------------------------------------
# Black-box style tests (no internal inspection)
# --------------------------------------------------------------------

def test_startup_creates_initial_tab(full_controller):
    ctrl, model, view, ds_panel, im_panel, tab_widget = full_controller
    # Observable: controller should have created one tab at init
    assert tab_widget.count() >= 1
    assert isinstance(model, DatasetList)


def test_add_tab_and_dataset_signal(qtbot, full_controller):
    ctrl, model, view, ds_panel, im_panel, tab_widget = full_controller

    # When adding a new tab via signal
    view.addTabSignal.emit("Map")
    assert tab_widget.count() >= 2

    # Add a dummy DataFrame to the model and emit datasetAdded
    import pandas as pd
    df = pd.DataFrame({"SDS_P1": [1, 2], "SDS_P2": [3, 4]})
    model.addDataset("Example", df)

    # Observable: panel should now list one dataset
    qtbot.waitUntil(lambda: ds_panel.dsList.count() == 1)
    assert ds_panel.dsList.count() == 1


def test_dataset_removal_flow(qtbot, full_controller):
    ctrl, model, view, ds_panel, im_panel, tab_widget = full_controller

    # Add dataset
    import pandas as pd
    df = pd.DataFrame({"SDS_P1": [1], "SDS_P2": [2]})
    model.addDataset("to_delete", df)
    qtbot.waitUntil(lambda: ds_panel.dsList.count() == 1)

    # Trigger datasetRemoved signal from panel
    item = ds_panel.dsList.item(0)
    label = ds_panel.dsList.itemWidget(item).label.text()

    with qtbot.waitSignal(model.datasetRemoved, timeout=2000):
        ds_panel.datasetRemoved.emit(label, 0)

    # Observable: dataset should be removed from model
    assert "to_delete" not in model.datasets


def test_update_imputation_flow(qtbot, full_controller):
    ctrl, model, view, ds_panel, im_panel, tab_widget = full_controller

    # Simulate imputation method change
    im_panel.createImputationItems(model.imputationMethods)
    im_panel.imputeMethodChanged.emit("SDS_P1", "Median")

    # Wait for model to register selection
    qtbot.wait(100)
    assert model.imputationSelection["SDS_P1"]["selection"] == "Median"


def test_close_tab_and_reopen(qtbot, full_controller):
    ctrl, model, view, ds_panel, im_panel, tab_widget = full_controller

    initial_count = tab_widget.count()
    ctrl.closeTab(0)
    qtbot.wait(100)
    ctrl.addTab("Plot")
    assert tab_widget.count() >= initial_count
