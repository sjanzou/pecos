from nose.tools import *
from os.path import abspath, dirname, join
import pecos
import numpy as np
import pandas as pd

testdir = dirname(abspath(__file__))
datadir = join(testdir,'data')

def test_time_integral():
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    data = np.array([[1,2,3], [4,5,6], [7,8,9], [10,11,12], [13,14,15]])
    df = pd.DataFrame(data=data, index=index, columns=['A', 'B', 'C'])
    
    df_integral = pecos.pv.time_integral(df)
    
    assert_equal(df_integral['Time integral of A'].values[0], 100800)
    assert_equal(df_integral['Time integral of B'].values[0], 115200)
    assert_equal(df_integral['Time integral of C'].values[0], 129600)
    
def test_qci_no_test_results():
    periods = 5
    np.random.seed(100)
    system_name = 'Test'
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    data=np.sin(np.random.rand(3,1)*np.arange(0,periods,1))
    df = pd.DataFrame(data=data.transpose(), index=index, columns=['A', 'B', 'C'])
    trans = dict(zip(df.columns, [[col] for col in df.columns]))
    
    pm = pecos.monitoring.PerformanceMonitoring()
    pm.add_dataframe(df, system_name)
    pm.add_translation_dictionary(trans, system_name)
    
    mask = pm.get_test_results_mask()
    QCI = pecos.metrics.qci(mask, per_day=False)
    
    assert_equal(mask.any().any(), True)
    assert_equal(QCI, 1)
    
def test_qci_with_test_results():
    periods = 5
    np.random.seed(100)
    system_name = 'Test'
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    data=np.sin(np.random.rand(3,1)*np.arange(0,periods,1))
    df = pd.DataFrame(data=data.transpose(), index=index, columns=['A', 'B', 'C'])
    trans = dict(zip(df.columns, [[col] for col in df.columns]))
    
    pm = pecos.monitoring.PerformanceMonitoring()
    pm.add_dataframe(df, system_name)
    pm.add_translation_dictionary(trans, system_name)
    
    test_result = {
    'System Name': 'Test',
    'Variable Name': 'A', 
    'Start Date': '2016-01-01 01:00:00', 
    'End Date': '2016-01-01 04:00:00', 
    'Timesteps': 4, 
    'Error Flag': 'Error Flag'}
    pm.test_results = pm.test_results.append(pd.DataFrame(test_result, index=[1]))
    
    test_result = {
    'System Name': 'Test',
    'Variable Name': 'B', 
    'Start Date': '2016-01-01 01:00:00', 
    'End Date': '2016-01-01 01:00:00', 
    'Timesteps': 1, 
    'Error Flag': 'Error Flag'}
    pm.test_results = pm.test_results.append(pd.DataFrame(test_result, index=[2]))
    
    mask = pm.get_test_results_mask()
    QCI = pecos.metrics.qci(mask, per_day = False)
    
    expected_mask = pd.DataFrame(data=[[False, False, True],[False, True, True],[False, True, True],[False, True, True],[False, True, True]], 
                                 index=pm.df.index, 
                                 columns=pm.df.columns)
    
    assert_equal((mask == expected_mask).any().any(), True)
    assert_equal(QCI, (15-5)/15.0)

    tfilter = pd.Series(data = [True, False, True, True, True], index=pm.df.index)
    QCI_with_tfilter = pecos.metrics.qci(mask, tfilter = tfilter, per_day=False)
    
    assert_equal(QCI_with_tfilter, (12-3)/12.0)
    
def test_qci_perday():
    periods = 48
    np.random.seed(100)
    system_name = 'Test'
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    data=np.sin(np.random.rand(3,1)*np.arange(0,periods,1))
    df = pd.DataFrame(data=data.transpose(), index=index, columns=['A', 'B', 'C'])
    trans = dict(zip(df.columns, [[col] for col in df.columns]))
    
    pm = pecos.monitoring.PerformanceMonitoring()
    pm.add_dataframe(df, system_name)
    pm.add_translation_dictionary(trans, system_name)
    
    test_result = {
    'System Name': 'Test',
    'Variable Name': 'A', 
    'Start Date': '2016-01-01 01:00:00', 
    'End Date': '2016-01-01 04:00:00', 
    'Timesteps': 4, 
    'Error Flag': 'Error Flag'}
    pm.test_results = pm.test_results.append(pd.DataFrame(test_result, index=[1]))
    
    test_result = {
    'System Name': 'Test',
    'Variable Name': 'B', 
    'Start Date': '2016-01-01 00:00:00', 
    'End Date': '2016-01-01 00:00:00', 
    'Timesteps': 1, 
    'Error Flag': 'Error Flag'}
    pm.test_results = pm.test_results.append(pd.DataFrame(test_result, index=[2]))
    
    mask = pm.get_test_results_mask()
    QCI = pecos.metrics.qci(mask, per_day = False)
    assert_equal(QCI, (144-5)/144.0)
    
    QCI = pecos.metrics.qci(mask, per_day = True)
    assert_equal(QCI['Quality Control Index'][0], (72-5)/72.0)
    assert_equal(QCI['Quality Control Index'][1], 1.0)
