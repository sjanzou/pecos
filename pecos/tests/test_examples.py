from nose.tools import *
from os.path import abspath, dirname, join
import os

testdir = dirname(abspath(__file__))
datadir = join(testdir,'data')

def test_simple_example():
    cwd = os.getcwd()
    exampledir = exampledir = join(testdir,'..', '..', 'examples', 'simple')
    
    os.chdir(exampledir)
    return_value = os.system('simple_example.py')
        
    os.chdir(cwd)
    
    assert_equals(return_value, 0)

def test_pv_example():
    cwd = os.getcwd()
    exampledir = exampledir = join(testdir,'..', '..', 'examples', 'pv')
    
    os.chdir(exampledir)
    return_value = os.system('pv_example.py')
        
    os.chdir(cwd)
    
    assert_equals(return_value, 0)
    
def test_metrics_example():
    cwd = os.getcwd()
    exampledir = exampledir = join(testdir,'..', '..', 'examples', 'metrics')
    
    os.chdir(exampledir)
    return_value = os.system('metrics_example.py')
        
    os.chdir(cwd)
    
    assert_equals(return_value, 0)

def test_dashboard_example():
    cwd = os.getcwd()
    exampledir = exampledir = join(testdir,'..', '..', 'examples', 'dashboard')
    
    os.chdir(exampledir)
    return_value = os.system('dashboard_example.py')
        
    os.chdir(cwd)
    
    assert_equals(return_value, 0)
