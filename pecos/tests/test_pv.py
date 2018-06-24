from nose.tools import *
from pandas.util.testing import assert_frame_equal
from os.path import abspath, dirname, join
import pandas as pd
import numpy as np
import pecos

testdir = dirname(abspath(__file__))
datadir = join(testdir,'data')

def test_insolation():
    # same test as metrics.time_integral
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    data = np.array([[1,2,3], [4,5,6], [7,8,9], [10,11,12], [13,14,15]])
    df = pd.DataFrame(data=data, index=index, columns=['A', 'B', 'C'])
    
    df_integral = pecos.pv.insolation(df)
    
    assert_equal(df_integral['Time integral of A'].values[0], 100800)
    assert_equal(df_integral['Time integral of B'].values[0], 115200)
    assert_equal(df_integral['Time integral of C'].values[0], 129600)

def test_energy():
    # same test as metrics.time_integral
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    data = np.array([[1,2,3], [4,5,6], [7,8,9], [10,11,12], [13,14,15]])
    df = pd.DataFrame(data=data, index=index, columns=['A', 'B', 'C'])
    
    df_integral = pecos.pv.energy(df)
    
    assert_equal(df_integral['Time integral of A'].values[0], 100800)
    assert_equal(df_integral['Time integral of B'].values[0], 115200)
    assert_equal(df_integral['Time integral of C'].values[0], 129600)
    
def test_performance_ratio():
    
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    E = pd.DataFrame(data=np.array([4, 4, 4.5, 2.7, 6]), index=index, columns=['Energy'])
    POA = pd.DataFrame(data=np.array([1000,1250,1250,900,1500]), index=index, columns=['POA'])
    
    PR = pecos.pv.performance_ratio(E, POA, 4, 1000)
    expected = pd.DataFrame(data=np.array([1.0, 0.8, 0.9, 0.75, 1.0]), index=index, columns=['Performance Ratio'])
    assert_frame_equal(PR, expected, check_dtype=False)

def test_normalized_current():
    
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    I = pd.DataFrame(data=np.array([4, 4, 4.5, 2.7, 6]), index=index, columns=['Current'])
    POA = pd.DataFrame(data=np.array([1000,1250,1250,900,1500]), index=index, columns=['POA'])
    
    NI = pecos.pv.normalized_current(I, POA, 4, 1000)
    expected = pd.DataFrame(data=np.array([1.0, 0.8, 0.9, 0.75, 1.0]), index=index, columns=['Normalized Current'])
    assert_frame_equal(NI, expected, check_dtype=False)
    
def test_normalized_efficiency():
    
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    P = pd.DataFrame(data=np.array([4, 4, 4.5, 2.7, 6]), index=index, columns=['Power'])
    POA = pd.DataFrame(data=np.array([1000,1250,1250,900,1500]), index=index, columns=['POA'])
    
    NE = pecos.pv.normalized_efficiency(P, POA, 4, 1000)
    expected = pd.DataFrame(data=np.array([1.0, 0.8, 0.9, 0.75, 1.0]), index=index, columns=['Normalized Efficiency'])
    assert_frame_equal(NE, expected, check_dtype=False)

def test_performance_index():
    
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    P = pd.DataFrame(data=np.array([4, 4, 4.5, 2.7, 6]), index=index, columns=['Power'])
    P_expected = pd.DataFrame(data=np.array([5,10,4.5,3,4]), index=index, columns=['Expected Power'])
    
    PI = pecos.pv.performance_index(P, P_expected)
    expected = pd.DataFrame(data=np.array([0.8,0.4,1,0.9,1.5]), index=index, columns=['Performance Index'])
    assert_frame_equal(PI, expected, check_dtype=False)

def test_energy_yield():
    
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    E = pd.DataFrame(data=np.array([4, 4, 4.5, 2.7, 6]), index=index, columns=['Energy'])
    
    EY = pecos.pv.energy_yield(E, 10)
    expected = pd.DataFrame(data=np.array([0.4,0.4,0.45,0.27,0.6]), index=index, columns=['Energy Yield'])
    assert_frame_equal(EY, expected, check_dtype=False)

def test_clearness_index():
    
    periods = 5
    index = pd.date_range('1/1/2016', periods=periods, freq='H')
    DNI = pd.DataFrame(data=np.array([4, 4, 4.5, 2.7, 6]), index=index, columns=['DNI'])
    ExI = pd.DataFrame(data=np.array([5,10,4.5,3,4]), index=index, columns=['ExI'])
    
    K = pecos.pv.clearness_index(DNI, ExI)
    expected = pd.DataFrame(data=np.array([0.8,0.4,1,0.9,1.5]), index=index, columns=['Clearness Index'])
    assert_frame_equal(K, expected, check_dtype=False)
