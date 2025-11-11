import pytest
import pandas as pd
from PyQt5.QtCore import QObject
from src.model.dataset_list import DatasetList
from src.model.strategy.average import Average
from src.model.strategy.backward_fill import BackwardFill
from src.model.strategy.forward_fill import ForwardFill
from src.model.strategy.median import Median


@pytest.fixture
def dataset_list():
    """Fixture: crea instancia limpia de DatasetList."""
    methods = {
        'Average' : Average(), 
        'Backward Fill' : BackwardFill(), 
        'Forward Fill' : ForwardFill(), 
        'Median' : Median(),
    }
    dl = DatasetList(methods)
    return dl

def test_tryName_generates_unique_name(dataset_list):
    dataset_list._DatasetList__datasets = {'data1': pd.DataFrame()}
    result = dataset_list.tryName('data1')
    assert result == 'data1(1)'


def test_genName_concatenates_addons(dataset_list):
    name = dataset_list.genName('base', ['extra', 'part'])
    assert name == 'base-extra-part'


def test_addDataset_adds_and_emits_signal(qtbot, dataset_list):
    df = pd.DataFrame({'a':[1,2], 'lat':[2,3], 'long' : [2,3]})
    with qtbot.waitSignal(dataset_list.datasetAdded, timeout=1000) as blocker:
        dataset_list.addDataset('datasetA', df)
    assert 'datasetA' in dataset_list.datasets
    assert blocker.args[0] == 'datasetA'


def test_renameDataset_success_emits_signal(qtbot, dataset_list):
    df = pd.DataFrame({'a':[1,2], 'lat':[2,3], 'long' : [2,3]})
    dataset_list._DatasetList__datasets = {'old': df}
    with qtbot.waitSignal(dataset_list.datasetRenamed, timeout=1000) as blocker:
        success = dataset_list.renameDataset('old', 'new')
    assert success is True
    assert 'new' in dataset_list.datasets
    assert blocker.args[0] == 'old'
    assert isinstance(blocker.args[1], dict)


def test_renameDataset_fails_for_empty_or_same_name(dataset_list):
    df = pd.DataFrame({'a':[1,2], 'lat':[2,3], 'long' : [2,3]})
    dataset_list._DatasetList__datasets = {'x': df}
    assert dataset_list.renameDataset('x', 'x') is False
    assert dataset_list.renameDataset('x', '') is False


def test_removeDataset_success_and_emit(qtbot, dataset_list):
    df = pd.DataFrame({'a':[1,2], 'lat':[2,3], 'long' : [2,3]})
    dataset_list._DatasetList__datasets = {'a': df}
    dataset_list._DatasetList__currentTab = type('t', (), {'selection':'a', 'results':{}})()
    with qtbot.waitSignal(dataset_list.datasetRemoved, timeout=1000):
        success = dataset_list.removeDataset('a')
    assert success is True
    assert 'a' not in dataset_list.datasets

def test_removeDataset_failure_returns_false(dataset_list):
    df = pd.DataFrame({'col':[1,2], 'lat':[2,3], 'long' : [2,3]})
    dataset_list._DatasetList__datasets = {'a': df}
    dataset_list._DatasetList__currentTab = type('t', (), {'selection':'a', 'results':{}})()
    assert dataset_list.removeDataset('nope') is False

def test_duplicateDataset_creates_copy(qtbot, dataset_list):
    df = pd.DataFrame({'SDS_P1':[1,2], 'SDS_P2':[3,4], 'lat':[2,3], 'long' : [2,3]})
    dataset_list._DatasetList__datasets = {'orig': df}
    with qtbot.waitSignal(dataset_list.datasetAdded, timeout=1000) as blocker:
        dataset_list.duplicateDataset('orig')
    assert blocker.args[0] == 'orig-duplicate'
    keys = list(dataset_list.datasets.keys())
    assert any('duplicate' in k for k in keys)
    new_key = [k for k in keys if 'duplicate' in k][0]
    pd.testing.assert_frame_equal(dataset_list.datasets[new_key], df)

def test_applyCorrection_applies_math(qtbot, dataset_list):
    df = pd.DataFrame({'SDS_P1':[10,20], 'SDS_P2':[30,40], 'lat':[2,3], 'long' : [2,3]})
    dataset_list._DatasetList__datasets = {'raw': df}
    with qtbot.waitSignal(dataset_list.datasetAdded, timeout=1000) as blocker:
        dataset_list.applyCorrection('raw', substract=10, division=10)
    assert blocker.args[0] == 'raw-corrected'
    keys = list(dataset_list.datasets.keys())
    assert any('corrected' in k for k in keys)
    corrected_df = dataset_list.datasets[keys[1]]
    assert corrected_df['SDS_P1'].iloc[0] == 0
    assert corrected_df['SDS_P2'].iloc[1] == 3

def test_saveFuseToCSV_creates_combined_csv(tmp_path, dataset_list):
    df1 = pd.DataFrame({'col':[1,2], 'lat':[2,3], 'long' : [2,3]})
    df2 = pd.DataFrame({'col':[3,4], 'lat':[2,3], 'long' : [2,3]})
    dataset_list._DatasetList__datasets = {'a':df1, 'b':df2}
    file = tmp_path / "combined.csv"
    dataset_list.saveFuseToCSV(['a','b'], file)
    result = pd.read_csv(file)
    assert len(result) == 4
    assert 'col' in result.columns


def test_loadFromCSV_reads_and_adds(qtbot, tmp_path, dataset_list):
    file = tmp_path / "data.csv"
    pd.DataFrame({'x':[1,2], 'lat':[2,3], 'long' : [2,3]}).to_csv(file, index=False)
    with qtbot.waitSignal(dataset_list.datasetAdded, timeout=1000) as blocker:
        dataset_list.loadFromCSV(str(file))
    assert blocker.args[0] == 'data'
    assert 'data' in dataset_list.datasets
    df = dataset_list.datasets['data']
    assert len(df) == 2

def test_loadFuseFromCSVs_combines_multiple(tmp_path, dataset_list):
    f1 = tmp_path / "f1.csv"
    f2 = tmp_path / "f2.csv"
    pd.DataFrame({'a':[1], 'lat':[3], 'long' : [5]}).to_csv(f1, index=False)
    pd.DataFrame({'a':[2], 'lat':[4], 'long' : [6]}).to_csv(f2, index=False)
    dataset_list.loadFuseFromCSVs([str(f1), str(f2)])
    key = list(dataset_list.datasets.keys())[0]
    assert 'Combined' in key
    df = dataset_list.datasets[key]
    assert len(df) == 2

