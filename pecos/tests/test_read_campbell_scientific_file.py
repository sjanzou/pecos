from nose.tools import *
from os.path import abspath, dirname, join
import pecos

testdir = dirname(abspath(inspect.getfile(inspect.currentframe())))
datadir = abspath(join(testdir, 'data'))    

def test_read_campbell_scientific():
    file_name = join(datadir,'TEST_db1_2014_01_01.dat')
    df = pecos.io.read_campbell_scientific(file_name, 'TIMESTAMP')
    assert_equals((48,11), df.shape)
    
if __name__ == '__main__':
    test_read_campbell_scientific()
