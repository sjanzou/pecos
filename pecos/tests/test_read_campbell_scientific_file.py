from nose.tools import *
from os.path import abspath, dirname, join
import yaml
import pecos

testdir = dirname(abspath(__file__))
datadir = join(testdir,'data')

config_file = join(datadir,'TEST_config.yml')
fid = open(config_file, 'r')
config = yaml.load(fid)
fid.close()
    
def test_read_campbell_scientific_file():
    file_name = join(datadir,'TEST_db1_2014_01_01.dat')
    df = pecos.read_campbell_scientific_file(file_name, 'TIMESTAMP')
    assert_equals((48,11), df.shape)
    
if __name__ == '__main__':
    test_read_campbell_scientific_file()
