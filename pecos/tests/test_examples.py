from nose.tools import *
from os.path import abspath, dirname, join
import os
import subprocess
import sys

testdir = dirname(abspath(__file__))
datadir = join(testdir,'data')

def test_simple_example():
    cwd = os.getcwd()
    exampledir = exampledir = join(testdir,'..', '..', 'examples', 'simple')
    
    os.chdir(exampledir)
    retcode = subprocess.call([sys.executable, 'simple_example.py'],  shell=True)
    os.chdir(cwd)
    
    assert_equals(retcode, 0)

def test_pv_example():
    cwd = os.getcwd()
    exampledir = exampledir = join(testdir,'..', '..', 'examples', 'pv')
    
    os.chdir(exampledir)
    retcode = subprocess.call([sys.executable, 'pv_example.py'],  shell=True)
    os.chdir(cwd)
    
    assert_equals(retcode, 0)
    
def test_metrics_example():
    cwd = os.getcwd()
    exampledir = exampledir = join(testdir,'..', '..', 'examples', 'metrics')
    
    os.chdir(exampledir)
    retcode = subprocess.call([sys.executable, 'metrics_example.py'],  shell=True)
    os.chdir(cwd)
    
    assert_equals(retcode, 0)

def test_dashboard_example():
    cwd = os.getcwd()
    exampledir = exampledir = join(testdir,'..', '..', 'examples', 'dashboard')
    
    os.chdir(exampledir)
    retcode = subprocess.call([sys.executable, 'dashboard_example.py'],  shell=True)
    os.chdir(cwd)
    
    assert_equals(retcode, 0)

if __name__ == '__main__':
    p = test_simple_example()