from nose.tools import *
from os.path import abspath, dirname, join, isfile
import pecos
import inspect

testdir = dirname(abspath(inspect.getfile(inspect.currentframe())))
datadir = abspath(join(testdir, 'data'))    

def test_read_campbell_scientific():
    file_name = join(datadir,'TEST_db1_2014_01_01.dat')
    assert_true(isfile(file_name))
    
    df = pecos.io.read_campbell_scientific(file_name, 'TIMESTAMP')
    assert_equals((48,11), df.shape)


#def test_write_dashboard():
#    filename = 'test_write_dashboard.html'
#    column_names = ['loc1', 'loc2']
#    row_names = ['sys1', 'sys2']
#    content = {}
#    content[('sys1', 'loc1')] = {'text': 'sys1-loc1 text'}
#    content[('sys1', 'loc2')] = {'text': 'sys1-loc2 text'}
#    content[('sys2', 'loc1')] = {'text': 'sys2-loc1 text'}
#    content[('sys2', 'loc2')] = {'text': 'sys2-loc2 text'}
#    
#    pecos.io.write_dashboard(filename, column_names, row_names, content)
