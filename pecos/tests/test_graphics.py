from nose.tools import *
from os.path import abspath, dirname, join, isfile
import os
import pecos
import pandas as pd
import numpy as np
import inspect
import matplotlib.pylab as plt

testdir = dirname(abspath(inspect.getfile(inspect.currentframe())))
datadir = abspath(join(testdir, 'data'))    

def test_plot_scatter1():
    filename = abspath(join(testdir, 'plot_scatter1.png'))
    if isfile(filename):
        os.remove(filename)
        
    x = pd.DataFrame({'x1' : pd.Series([1., 2., 3.], index=['a', 'b', 'c'])})
    y = pd.DataFrame({'y1' : pd.Series([1., 2., 3.], index=['a', 'b', 'c'])})
    
    plt.figure()
    pecos.graphics.plot_scatter(x,y,xaxis_min=0.5, xaxis_max=6.5, yaxis_min=0.5, yaxis_max=3.5)
    plt.savefig(filename, format='png')
    plt.close()
    
    assert_true(isfile(filename))

def test_plot_scatter2():
    filename = abspath(join(testdir, 'plot_scatter2.png'))
    if isfile(filename):
        os.remove(filename)
        
    x = pd.DataFrame({'x1' : pd.Series([1., 2., 3.], index=['a', 'b', 'c']),
         'x2' : pd.Series([4., 5., 6.], index=['a', 'b', 'c'])})
    y = pd.DataFrame({'y1' : pd.Series([1., 2., 3.], index=['a', 'b', 'c'])})
    
    plt.figure()
    pecos.graphics.plot_scatter(x,y,xaxis_min=0.5, xaxis_max=6.5, yaxis_min=0.5, yaxis_max=3.5)
    plt.savefig(filename, format='png')
    plt.close()
    
    assert_true(isfile(filename))

def test_plot_scatter3():
    filename = abspath(join(testdir, 'plot_scatter3.png'))
    if isfile(filename):
        os.remove(filename)
        
    y = pd.DataFrame({'y1' : pd.Series([1., 2., 3.], index=['a', 'b', 'c']),
         'y2' : pd.Series([4., 5., 6.], index=['a', 'b', 'c'])})
    x = pd.DataFrame({'x1' : pd.Series([1., 2., 3.], index=['a', 'b', 'c'])})
    
    plt.figure()
    pecos.graphics.plot_scatter(x,y,xaxis_min=0.5, xaxis_max=3.5, yaxis_min=0.5, yaxis_max=6.5)
    plt.savefig(filename, format='png')
    plt.close()
    
    assert_true(isfile(filename))
    
def test_plot_timeseries1():
    filename = abspath(join(testdir, 'plot_timeseries1.png'))
    if isfile(filename):
        os.remove(filename)
        
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    data = np.array([[1,2,3], [4,5,6], [7,8,9], [10,11,12], [13,14,15]])
    df = pd.DataFrame(data=data, index=index, columns=['A', 'B', 'C'])
    
    plt.figure()
    pecos.graphics.plot_timeseries(df,yaxis_min=0, yaxis_max=20)
    plt.savefig(filename, format='png')
    plt.close()
    
    assert_true(isfile(filename))
    
def test_plot_timeseries2():
    filename = abspath(join(testdir, 'plot_timeseries2.png'))
    if isfile(filename):
        os.remove(filename)
        
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    data = np.array([[1,2,3], [4,5,6], [7,8,9], [10,11,12], [13,14,15]])
    df = pd.DataFrame(data=data, index=index, columns=['A', 'B', 'C'])
    tfilter = pd.Series(data = (df.index < index[3]), index = df.index)
    
    plt.figure()
    pecos.graphics.plot_timeseries(df,tfilter, yaxis_min=0, yaxis_max=20)
    plt.savefig(filename, format='png')
    plt.close()
    
    assert_true(isfile(filename))

def test_plot_test_results1():
    filename_root = abspath(join(testdir, 'plot_test_results1'))
    pm = pecos.monitoring.PerformanceMonitoring()
    
    graphics = pecos.graphics.plot_test_results(filename_root, pm)
    
    assert_equals(graphics,[])

def test_plot_test_results2():
    filename_root = abspath(join(testdir, 'plot_test_results2'))
    pm = pecos.monitoring.PerformanceMonitoring()
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    data = np.array([[1,2,3], [4,5,6], [7,8,9], [10,11,12], [13,14,15]])
    df = pd.DataFrame(data=data, index=index, columns=['A', 'B', 'C'])
    tfilter = pd.Series(data = (df.index < index[3]), index = df.index)
    
    pm.add_dataframe(df, 'test', True)
    pm.add_time_filter(tfilter)
    
    pm.check_range([0,7]) # 2 test failures
    
    graphics = pecos.graphics.plot_test_results(filename_root, pm)
    
    assert_equals(len(graphics),2)

    