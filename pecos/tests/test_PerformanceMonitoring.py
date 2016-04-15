import unittest
from nose.tools import *
from os.path import abspath, dirname, join
import pecos
import datetime

testdir = dirname(abspath(__file__))
datadir = join(testdir,'data')

class Test_db1_file(unittest.TestCase):

    @classmethod
    def setUp(self):
        trans = {
        'Range': ['Range1', 'Range2'],
        'Deviation': ['Deviation1'],
        'Corrupt': ['Corrupt1'],
        'Missing': ['Missing1', 'Missing2'],
        'All': ['Range1', 'Range2', 'Deviation1', 'Corrupt1', 'Missing1', 'Missing2'],
        'Composite': ['(R1-sum(M))/R1', '(R2-sum(M))/R2', 'M1*D^2', 'M2*D^2', 'mean(All)-10']}
        
        self.composite_signals = [
        {'Comp1 (R-sum(M))/R': 'np.divide(({Range} - {Missing}.sum(axis=1)),{Range})'},
        {'Comp2 M*D^2': '{Missing}*np.power({Deviation},2)'},
        {'Comp3 mean(ALL)-10': '({All}).mean(axis=1) - 10'}]
        
        self.file_date = [datetime.datetime(2014, 1, 1, 0, 0, 0)]
        
        system_name = 'TEST_db1'
        file_name = join(datadir,'TEST_db1_2014_01_01.dat')
        df = pecos.io.read_campbell_scientific(file_name, 'TIMESTAMP')
        self.pm = pecos.monitoring.PerformanceMonitoring()
        self.pm.add_dataframe(df, system_name)
        self.pm.add_translation_dictonary(trans, system_name)

    @classmethod
    def tearDown(self):
        pass
        
    def test_check_timestamp(self):
        self.pm.check_timestamp(3600) # 1 hour data
        test_results = self.pm.test_results
        """
      System Name Variable Name          Start Date            End Date  \
    0                           2014-01-01 04:00:00 2014-01-01 03:00:00
    1                           2014-01-02 10:00:00 2014-01-02 10:00:00
    2                           2014-01-02 20:00:00 2014-01-02 20:00:00
    3                           2014-01-01 03:00:00 2014-01-01 03:00:00
    4                           2014-01-01 04:00:00 2014-01-01 04:00:00
    5                           2014-01-01 18:00:00 2014-01-01 18:00:00
    6                           2014-01-01 02:00:00 2014-01-01 02:00:00
    7                           2014-01-02 15:00:00 2014-01-02 17:00:00
    
       Timesteps              Error Flag
    0        2.0  Nonmonotonic timestamp
    1        1.0  Nonmonotonic timestamp
    2        1.0  Nonmonotonic timestamp
    3        1.0     Duplicate timestamp
    4        1.0     Duplicate timestamp
    5        2.0     Duplicate timestamp
    6        1.0       Missing timestamp
    7        3.0       Missing timestamp
        """
        assert_equal(sum(test_results['Error Flag'] == 'Nonmonotonic timestamp'), 3)
        assert_equal(sum(test_results['Error Flag'] == 'Duplicate timestamp'), 3)
        assert_equal(sum(test_results['Error Flag'] == 'Missing timestamp'), 2)
        assert_equal(sum(test_results['Timesteps']), 12)

    def test_check_missing(self):
        self.pm.check_missing()
        temp = self.pm.test_results[self.pm.test_results['Error Flag'] == 'Missing data']
        """
      System Name      Variable Name  \
    0              TEST_db1:Missing1
    1              TEST_db1:Missing2
    2              TEST_db1:M1*D^2
    3              TEST_db1:M2*D^2
    
               Start Date  \
    0 2014-01-01 06:00:00
    1 2014-01-02 08:00:00
    2 2014-01-01 06:00:00
    3 2014-01-02 08:00:00
    
                 End Date  Timesteps  \
    0 2014-01-01 15:00:00  10
    1 2014-01-02 12:00:00  5
    2 2014-01-01 15:00:00  10
    3 2014-01-02 12:00:00  5
    
         Error Flag
    0  Missing data
    1  Missing data
    2  Missing data
    3  Missing data
        """
        expected = [10,5,10,5]
        assert_equal(temp['Timesteps'].values.tolist(), expected)
    
    def test_check_corrupt(self):
        self.pm.check_timestamp(3600)
        self.pm.check_corrupt([-999])
        temp = self.pm.test_results[self.pm.test_results['Error Flag'] == 'Corrupt data']
    
        """
          System Name       Variable Name          Start Date            End Date Timesteps    Error Flag
    0              TEST_db1:Corrupt1 2014-01-01 11:00:00 2014-01-01 11:00:00         1  Corrupt Data
    1              TEST_db1:Corrupt1 2014-01-02 09:00:00 2014-01-02 10:00:00         2  Corrupt Data
        """
        expected = [1,2]
        assert_equal(temp['Timesteps'].values.tolist(), expected)
    
    def test_check_range(self):
        self.pm.check_timestamp(3600)
        self.pm.check_range([1,3],'Range')
        test_results = self.pm.test_results
        
        assert_equal(test_results[test_results['Variable Name'] == 'Range1'].shape[0], 3)
        assert_equal(test_results[test_results['Variable Name'] == 'Range2'].shape[0], 3)
    
    def test_check_increment(self):
        self.pm.check_timestamp(3600)
        self.pm.check_increment([None,8],'Range')
        self.pm.check_increment([-8,None],'Range', absolute_value = False)
        test_results = self.pm.test_results
    
        assert_equal(test_results['Error Flag'][test_results['Error Flag'] == 'Increment > upper bound, 8'].shape[0], 2)
        assert_equal(test_results['Error Flag'][test_results['Error Flag'] == 'Increment < lower bound, -8'].shape[0], 1)
        
    def test_get_elapsed_time(self):
        elapsed_time = self.pm.get_elapsed_time()

        expected = [75600, 79200, 82800, 86400, 90000, 93600, 97200, 100800, 104400, 108000]
        assert_equal(elapsed_time.iloc[24:34][0].values.tolist(), expected)
        
    def test_get_clock_time(self):
        clock_time = self.pm.get_clock_time()
        
        expected = [75600, 79200, 82800, 0, 3600, 7200, 10800, 14400, 18000, 21600]
        assert_equal(clock_time.iloc[24:34][0].values.tolist(), expected)
