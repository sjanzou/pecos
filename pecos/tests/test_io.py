from nose.tools import *
from os.path import abspath, dirname, join, isfile
import pecos
import pandas as pd
import os
import numpy as np
import inspect


testdir = dirname(abspath(inspect.getfile(inspect.currentframe())))
datadir = abspath(join(testdir, 'data'))    

def test_read_campbell_scientific():
    file_name = join(datadir,'TEST_db1_2014_01_01.dat')
    assert_true(isfile(file_name))
    
    df = pecos.io.read_campbell_scientific(file_name, 'TIMESTAMP')
    assert_equals((48,11), df.shape)

def test_write_metrics1():
    filename = abspath(join(testdir, 'test_write_metrics1.csv'))
    if isfile(filename):
        os.remove(filename)
        
    metrics = pd.DataFrame({'metric1' : pd.Series([1.], index=[pd.datetime(2016,1,1)])})
    pecos.io.write_metrics(filename, metrics)
    assert_true(isfile(filename))
    
    from_file1 = pd.read_csv(filename)
    assert_equals(from_file1.shape, (1,2))
    
    # append another date
    metrics = pd.DataFrame({'metric1' : pd.Series([2.], index=[pd.datetime(2016,1,2)])})
    pecos.io.write_metrics(filename, metrics)
    
    from_file2 = pd.read_csv(filename)
    assert_equals(from_file2.shape, (2,2))
    
    # append another metric
    metrics = pd.DataFrame({'metric2' : pd.Series([3.], index=[pd.datetime(2016,1,2)])})
    pecos.io.write_metrics(filename, metrics)
    
    from_file3= pd.read_csv(filename)
    assert_equals(from_file3.shape, (2,3))

def test_write_test_results1():
    filename = abspath(join(testdir, 'test_write_test_results1.csv'))
    if isfile(filename):
        os.remove(filename)
        
    pm = pecos.monitoring.PerformanceMonitoring()
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    data = np.array([[1,2,3], [4,5,6], [7,8,9], [10,11,12], [13,14,15]])
    df = pd.DataFrame(data=data, index=index, columns=['A', 'B', 'C'])
    tfilter = pd.Series(data = (df.index < index[3]), index = df.index)
    pm.add_dataframe(df, 'test', True)
    pm.add_time_filter(tfilter)    
    pm.check_range([0,7]) # 2 test failures
    
    pecos.io.write_test_results(filename, pm.test_results)
    from_file = pd.read_csv(filename)
    
    assert_true(isfile(filename))
    assert_equals(from_file.shape, (2,7))

def test_write_monitoring_report1():
    filename = abspath(join(testdir, 'test_write_monitoring_report1.html'))
    if isfile(filename):
        os.remove(filename)
        
    pm = pecos.monitoring.PerformanceMonitoring()
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    data = np.array([[1,2,3], [4,5,6], [7,8,9], [10,11,12], [13,14,15]])
    df = pd.DataFrame(data=data, index=index, columns=['A', 'B', 'C'])
    tfilter = pd.Series(data = (df.index < index[3]), index = df.index)
    pm.add_dataframe(df, 'test', True)
    pm.add_time_filter(tfilter)    
    pm.check_range([0,7]) # 2 test failures
    
    pecos.io.write_monitoring_report(filename, pm)
    
    assert_true(isfile(filename))
    
def test_write_dashboard1():
    filename = abspath(join(testdir, 'test_write_dashboard1.html'))
    if isfile(filename):
        os.remove(filename)
        
    column_names = ['loc1', 'loc2']
    row_names = ['sys1', 'sys2']
    content = {}
    content[('sys1', 'loc1')] = {'text': 'sys1-loc1 text'}
    content[('sys1', 'loc2')] = {'text': 'sys1-loc2 text'}
    content[('sys2', 'loc1')] = {'text': 'sys2-loc1 text'}
    content[('sys2', 'loc2')] = {'text': 'sys2-loc2 text'}
    
    pecos.io.write_dashboard(filename, column_names, row_names, content)
    
    assert_true(isfile(filename))

