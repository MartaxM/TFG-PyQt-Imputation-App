import pytest
import pandas as pd
from PyQt5.QtCore import QObject
from src.model.dataset_list import DatasetList
from src.model.tab_info import TabInfo
from src.model.strategy.average import Average
from src.model.strategy.backward_fill import BackwardFill
from src.model.strategy.forward_fill import ForwardFill
from src.model.strategy.median import Median

@pytest.fixture
def dataset_list():
    """Basic DatasetList"""
    methods = {
        'Average' : Average(), 
        'Backward Fill' : BackwardFill(), 
        'Forward Fill' : ForwardFill(), 
        'Median' : Median(),
    }

    dl = DatasetList(methods)
    return dl


@pytest.fixture
def mock_tab():
    """Create basic Tab"""
    return TabInfo(type='Default', variables = ['SDS_P1', 'SDS_P2'], startingMethod = 'Average')

# _clearWorking 

def test__clearWorking_clears_all(qtbot, dataset_list, mock_tab):
    mock_tab.results = {"a": 1, "b": 2}
    dataset_list._DatasetList__currentTab = mock_tab
    with qtbot.waitSignal(dataset_list.clearResult, timeout=1000):
        dataset_list._clearWorking()
    assert mock_tab.results == {}


def test__clearWorking_specific_variable(qtbot, dataset_list, mock_tab):
    mock_tab.results = {"x": 1, "y": 2}
    dataset_list._DatasetList__currentTab = mock_tab
    with qtbot.waitSignal(dataset_list.clearResult, timeout=1000):
        dataset_list._clearWorking("x")
    assert "y" in mock_tab.results


# changeImputationSelection

def test_changeImputationSelection_updates_and_emits(qtbot, dataset_list, mock_tab, monkeypatch):
    dataset_list._DatasetList__currentTab = mock_tab
    dataset_list._DatasetList__datasets = {"data1": pd.DataFrame({"SDS_P1": [1, None, 3]})}
    dataset_list._DatasetList__currentTab.selection = "data1"
    # Avoid real imputation 
    called = {}
    monkeypatch.setattr(dataset_list, "impute", lambda var: called.update({var: True}))

    variable = "SDS_P1"
    method = "Median"
    dataset_list._DatasetList__currentTab._TabInfo__imputationSelection[variable]["visible"] = True
    dataset_list._DatasetList__currentTab._TabInfo__imputationSelection[variable]["selection"] = "Average"
    
    with qtbot.waitSignal(dataset_list.imputationChanged, timeout=1000):
        dataset_list.changeImputationSelection(variable, method)

    assert called["SDS_P1"]
    assert dataset_list._DatasetList__currentTab._TabInfo__imputationSelection[variable]["selection"] == method


def test_changeImputationSelection_ignores_invalid(dataset_list, mock_tab):
    dataset_list._DatasetList__currentTab = mock_tab
    dataset_list.changeImputationSelection("X", "UnknownMethod")  # No error should be raised


# changeImputationVisiblity

def test_changeImputationVisiblity_triggers_reimpute(qtbot, dataset_list, mock_tab, monkeypatch):
    dataset_list._DatasetList__currentTab = mock_tab
    dataset_list._DatasetList__datasets = {"data1": pd.DataFrame({"SDS_P1": [1, None, 3]})}
    dataset_list.setCurrent('data1')

    called = {}
    monkeypatch.setattr(dataset_list, "impute", lambda var: called.update({var: True}))

    variable = "SDS_P1"
    with qtbot.waitSignal(dataset_list.imputationVisible, timeout=1000) as blocker:
        dataset_list.changeImputationVisiblity(variable, True)

    assert called["SDS_P1"]
    assert blocker.args == [variable, True]
    assert dataset_list._DatasetList__currentTab._TabInfo__imputationSelection[variable]["visible"] is True


# changeDatasetVisiblity

def test_changeDatasetVisiblity_adds_and_emits(qtbot, dataset_list, mock_tab):
    dataset_list._DatasetList__currentTab = mock_tab
    with qtbot.waitSignal(dataset_list.datasetVisilityChanged, timeout=1000):
        dataset_list.changeDatasetVisiblity("set1", True)
    assert "set1" in mock_tab.visible


def test_changeDatasetVisiblity_removes_and_emits(qtbot, dataset_list, mock_tab):
    mock_tab.visible = ["set1"]
    dataset_list._DatasetList__currentTab = mock_tab
    with qtbot.waitSignal(dataset_list.datasetVisilityChanged, timeout=1000):
        dataset_list.changeDatasetVisiblity("set1", False)
    assert "set1" not in mock_tab.visible


# changeTab

def test_changeTab_sets_current_and_emits(qtbot, dataset_list):
    t1 = TabInfo("Default", variables = ['SDS_P1', 'SDS_P2'], startingMethod = 'Average')
    dataset_list._DatasetList__tabs = [t1]
    with qtbot.waitSignal(dataset_list.currentTabChanged, timeout=1000) as blocker:
        dataset_list.changeTab(0)
    assert dataset_list.currentTab == t1
    assert blocker.args == [0]


def test_changeTab_out_of_range_sets_none(dataset_list):
    dataset_list._DatasetList__tabs = []
    dataset_list.changeTab(5)
    assert dataset_list.currentTab is None


# comparation related

def test_rootMeanSquaredError_returns_valid_value(dataset_list):
    import numpy as np
    df1 = pd.DataFrame({"SDS_P1": [1, 2, 3]})
    df2 = pd.DataFrame({"SDS_P1": [1, 1, 1]})
    rmse = dataset_list.rootMeanSquaredError(df1, df2, "SDS_P1")
    assert pytest.approx(rmse, 0.1) == np.sqrt(((df1["SDS_P1"] - df2["SDS_P1"])**2).mean())

# get results

def test_getResults_returns_copy(dataset_list, mock_tab):
    mock_tab.results = {"SDS_P1": 1}
    dataset_list._DatasetList__currentTab = mock_tab
    result = dataset_list.getResults()
    assert result == {"SDS_P1": 1}
    assert result is not mock_tab.results

def test_getVarResult_returns_correct_value(dataset_list, mock_tab):
    mock_tab.results = {"SDS_P1": pd.DataFrame({"x": [1]})}
    dataset_list._DatasetList__currentTab = mock_tab
    res = dataset_list.getVarResult("SDS_P1")
    assert isinstance(res, pd.DataFrame)
    assert "x" in res.columns
