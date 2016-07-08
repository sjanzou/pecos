import unittest
from nose.tools import *
from os.path import abspath, dirname, join
import pecos
import pandas as pd
from pandas.util.testing import assert_frame_equal
import numpy as np

#pd.set_option('expand_frame_repr', False)

testdir = dirname(abspath(__file__))
datadir = join(testdir,'data')
simpleexampledir = join(testdir,'..', '..', 'examples','simple')

def simple_example_run_analysis(df):
    # Input
    system_name = 'Simple'
    translation_dictionary = {
        'Linear': ['A'],
        'Random': ['B'],
        'Wave': ['C','D']}
    expected_frequency = 900 # s
    corrupt_values = [-999]
    range_bounds = {
        'Random': [0, 1],
        'Wave': [-1, 1],
        'Wave Absolute Error': [None, 0.25]}
    increment_bounds = {
        'Linear': [0.0001, None],
        'Random': [0.0001, None],
        'Wave': [0.0001, 0.6]}
        
     # Define output files
    metrics_file = join(testdir, system_name + '_metrics.csv')
    test_results_file = join(testdir, system_name + '_test_results.csv')

    # Create an PerformanceMonitoring instance
    pm = pecos.monitoring.PerformanceMonitoring()
    
    # Populate the PerformanceMonitoring instance
    pm.add_dataframe(df, system_name)
    pm.add_translation_dictionary(translation_dictionary, system_name)
    
    # Check timestamp
    pm.check_timestamp(expected_frequency)
     
    # Generate time filter
    clock_time = pm.get_clock_time()
    time_filter = (clock_time > 3*3600) & (clock_time < 21*3600)
    pm.add_time_filter(time_filter)
    
    # Check missing
    pm.check_missing()
            
    # Check corrupt
    pm.check_corrupt(corrupt_values) 
    
    # Add composite signals
    elapsed_time= pm.get_elapsed_time()
    wave_model = np.sin(10*(elapsed_time/86400))
    wave_model.columns=['Wave Model']
    pm.add_signal('Wave Model', wave_model)
    wave_model_abs_error = np.abs(np.subtract(pm.df[pm.trans['Wave']], wave_model))
    wave_model_abs_error.columns=['Wave Absolute Error C', 'Wave Absolute Error D']
    pm.add_signal('Wave Absolute Error', wave_model_abs_error)
    
    # Check range
    for key,value in range_bounds.items():
        pm.check_range(value, key)
    
    # Check increment
    for key,value in increment_bounds.items():
        pm.check_increment(value, key) 
        
    # Compute metrics
    mask = pm.get_test_results_mask()
    QCI = pecos.metrics.qci(mask, pm.tfilter)
    
    # Write metrics, test results, and report files
    pecos.io.write_metrics(metrics_file, QCI)
    pecos.io.write_test_results(test_results_file, pm.test_results)
    
    return QCI, test_results_file
    
class Test_simple_example(unittest.TestCase):

    @classmethod
    def setUp(self):
        trans = {
            'Linear': ['A'],
            'Random': ['B'],
            'Wave': ['C','D']}
            
        system_name = 'Simple'
        file_name = join(simpleexampledir,'simple.xlsx')

        df = pd.read_excel(file_name)
        self.pm = pecos.monitoring.PerformanceMonitoring()
        self.pm.add_dataframe(df, system_name)
        self.pm.add_translation_dictionary(trans, system_name)
        self.pm.check_timestamp(900) 
        clock_time = self.pm.get_clock_time()
        time_filter = (clock_time > 3*3600) & (clock_time < 21*3600)
        self.pm.add_time_filter(time_filter)
        
    @classmethod
    def tearDown(self):
        pass
        
    def test_check_timestamp(self):
        test_results = self.pm.test_results

        """
        Missing timestamp at 5:00
        Duplicate timestamp 17:00
        Non-monotonic timestamp 19:30
        """
        expected = pd.DataFrame(
            [('', '', pd.Timestamp('2015-01-01 19:30:00'), pd.Timestamp('2015-01-01 19:30:00'), 1.0, 'Nonmonotonic timestamp'),
             ('', '', pd.Timestamp('2015-01-01 17:00:00'), pd.Timestamp('2015-01-01 17:00:00'), 1.0, 'Duplicate timestamp'),
             ('', '', pd.Timestamp('2015-01-01 05:00:00'), pd.Timestamp('2015-01-01 05:00:00'), 1.0, 'Missing timestamp')],
            columns=['System Name', 'Variable Name', 'Start Date', 'End Date', 'Timesteps', 'Error Flag'])
        
        
        assert_frame_equal(test_results, expected, check_dtype=False)
        
    def test_check_missing(self):
        self.pm.check_missing()
        temp = self.pm.test_results[self.pm.test_results['Error Flag'] == 'Missing data']
        temp.index = np.arange(temp.shape[0])
        
        """
        Column D is missing data from 17:45 until 18:15
        """
        expected = pd.DataFrame(
            [('Simple', 'D', pd.Timestamp('2015-01-01 17:45:00'), pd.Timestamp('2015-01-01 18:15:00'), 3.0, 'Missing data')],
            columns=['System Name', 'Variable Name', 'Start Date', 'End Date', 'Timesteps', 'Error Flag'])

        assert_frame_equal(temp, expected, check_dtype=False)
    
    def test_check_corrupt(self):
        self.pm.check_corrupt([-999])
        temp = self.pm.test_results[self.pm.test_results['Error Flag'] == 'Corrupt data']
        temp.index = np.arange(temp.shape[0])
        
        """
        Column C has corrupt data (-999) between 7:30 and 9:30
        """
        expected = pd.DataFrame(
            [('Simple', 'C', pd.Timestamp('2015-01-01 07:30:00'), pd.Timestamp('2015-01-01 09:30:00'), 9.0, 'Corrupt data')],
            columns=['System Name', 'Variable Name', 'Start Date', 'End Date', 'Timesteps', 'Error Flag'])
        
        assert_frame_equal(temp, expected, check_dtype=False)
        
    def test_check_range(self):
        self.pm.check_corrupt([-999])
        self.pm.check_range([0, 1], 'Random')
        self.pm.check_range([-1, 1], 'Wave')
        
        temp = self.pm.test_results[['Data' in ef for ef in self.pm.test_results['Error Flag']]]
        temp.index = np.arange(temp.shape[0])
        
        """
        Column B is below the expected lower bound of 0 at 6:30 and above the expected upper bound of 1 at 15:30
        Column D is occasionally below the expected lower bound of -1 around midday (2 timesteps) and above the expected upper bound of 1 in the early morning and late evening (10 timesteps).
        """
        expected = pd.DataFrame(
            [('Simple', 'B', pd.Timestamp('2015-01-01 06:30:00'), pd.Timestamp('2015-01-01 06:30:00'), 1.0, 'Data < lower bound, 0'),
             ('Simple', 'B', pd.Timestamp('2015-01-01 15:30:00'), pd.Timestamp('2015-01-01 15:30:00'), 1.0, 'Data > upper bound, 1'),
             ('Simple', 'D', pd.Timestamp('2015-01-01 11:15:00'), pd.Timestamp('2015-01-01 11:15:00'), 1.0, 'Data < lower bound, -1'),
             ('Simple', 'D', pd.Timestamp('2015-01-01 12:45:00'), pd.Timestamp('2015-01-01 12:45:00'), 1.0, 'Data < lower bound, -1'),
             ('Simple', 'D', pd.Timestamp('2015-01-01 03:15:00'), pd.Timestamp('2015-01-01 03:30:00'), 2.0, 'Data > upper bound, 1'),
             ('Simple', 'D', pd.Timestamp('2015-01-01 04:00:00'), pd.Timestamp('2015-01-01 04:00:00'), 1.0, 'Data > upper bound, 1'),
             ('Simple', 'D', pd.Timestamp('2015-01-01 04:30:00'), pd.Timestamp('2015-01-01 04:45:00'), 2.0, 'Data > upper bound, 1'),
             ('Simple', 'D', pd.Timestamp('2015-01-01 18:30:00'), pd.Timestamp('2015-01-01 18:45:00'), 2.0, 'Data > upper bound, 1'),
             ('Simple', 'D', pd.Timestamp('2015-01-01 19:15:00'), pd.Timestamp('2015-01-01 19:45:00'), 3.0, 'Data > upper bound, 1')],
            columns=['System Name', 'Variable Name', 'Start Date', 'End Date', 'Timesteps', 'Error Flag'])
        
        assert_frame_equal(temp, expected, check_dtype=False)
    
    def test_check_increment(self):
        self.pm.check_corrupt([-999])
        self.pm.check_increment([0.0001, None], 'Linear')
        self.pm.check_increment([0.0001, None], 'Random')
        self.pm.check_increment([0.0001, 0.6], 'Wave')
        
        temp = self.pm.test_results[['Increment' in ef for ef in self.pm.test_results['Error Flag']]]
        temp.index = np.arange(temp.shape[0])
        
        """
        Column A has the same value (0.5) from 12:00 until 14:30
        Column C does not follow the expected sine function from 13:00 until 16:15. The change is abrupt and gradually corrected.
        """
        expected = pd.DataFrame(
            [('Simple', 'A', pd.Timestamp('2015-01-01 12:15:00'), pd.Timestamp('2015-01-01 14:30:00'), 10.0, 'Increment < lower bound, 0.0001'),
             ('Simple', 'C', pd.Timestamp('2015-01-01 13:00:00'), pd.Timestamp('2015-01-01 13:00:00'), 1.0, 'Increment > upper bound, 0.6')],
            columns=['System Name', 'Variable Name', 'Start Date', 'End Date', 'Timesteps', 'Error Flag'])
        
        assert_frame_equal(temp, expected, check_dtype=False)
        
    def test_composite_signal(self):
        self.pm.check_corrupt([-999])
        
        elapsed_time = self.pm.get_elapsed_time()
        wave_model = np.sin(10*(elapsed_time/86400))
        wave_model.columns=['Wave Model']
        self.pm.add_signal('Wave Model', wave_model)
        wave_model_abs_error = np.abs(np.subtract(self.pm.df[self.pm.trans['Wave']], wave_model))
        wave_model_abs_error.columns=['Wave Absolute Error C', 'Wave Absolute Error D']
        self.pm.add_signal('Wave Absolute Error', wave_model_abs_error)
        
        self.pm.check_range([None, 0.25], 'Wave Absolute Error')
        
        temp = self.pm.test_results[['Data' in ef for ef in self.pm.test_results['Error Flag']]]
        temp.index = np.arange(temp.shape[0])
        
        expected = pd.DataFrame(
            [('','Wave Absolute Error C',pd.Timestamp('2015-01-01 13:00:00'),pd.Timestamp('2015-01-01 14:45:00'),8.0,'Data > upper bound, 0.25')],
            columns=['System Name', 'Variable Name', 'Start Date', 'End Date', 'Timesteps', 'Error Flag'])
        
        assert_frame_equal(temp, expected, check_dtype=False)
        
    def test_full_example(self):
        data_file = join(simpleexampledir,'simple.xlsx')
        df = pd.read_excel(data_file)
        
        (QCI, test_results_file) = simple_example_run_analysis(df)
    
        """
           System Name          Variable Name           Start Date             End Date Timesteps                       Error Flag
1                                      2015-01-01 19:30:00  2015-01-01 19:30:00         1           Nonmonotonic timestamp
2                                      2015-01-01 17:00:00  2015-01-01 17:00:00         1              Duplicate timestamp
3                                      2015-01-01 05:00:00  2015-01-01 05:00:00         1                Missing timestamp
4               Wave Absolute Error C  2015-01-01 13:00:00  2015-01-01 14:45:00         8         Data > upper bound, 0.25
5       Simple                      A  2015-01-01 12:15:00  2015-01-01 14:30:00        10  Increment < lower bound, 0.0001
6       Simple                      B  2015-01-01 06:30:00  2015-01-01 06:30:00         1            Data < lower bound, 0
7       Simple                      B  2015-01-01 15:30:00  2015-01-01 15:30:00         1            Data > upper bound, 1
8       Simple                      C  2015-01-01 07:30:00  2015-01-01 09:30:00         9                     Corrupt data
9       Simple                      C  2015-01-01 13:00:00  2015-01-01 13:00:00         1     Increment > upper bound, 0.6
10      Simple                      D  2015-01-01 17:45:00  2015-01-01 18:15:00         3                     Missing data
11      Simple                      D  2015-01-01 11:15:00  2015-01-01 11:15:00         1           Data < lower bound, -1
12      Simple                      D  2015-01-01 12:45:00  2015-01-01 12:45:00         1           Data < lower bound, -1
13      Simple                      D  2015-01-01 03:15:00  2015-01-01 03:30:00         2            Data > upper bound, 1
14      Simple                      D  2015-01-01 04:00:00  2015-01-01 04:00:00         1            Data > upper bound, 1
15      Simple                      D  2015-01-01 04:30:00  2015-01-01 04:45:00         2            Data > upper bound, 1
16      Simple                      D  2015-01-01 18:30:00  2015-01-01 18:45:00         2            Data > upper bound, 1
17      Simple                      D  2015-01-01 19:15:00  2015-01-01 19:45:00         3            Data > upper bound, 1
"""
        
        assert_almost_equal(QCI.iloc[0,0],0.871227,6)
        
        actual = pd.read_csv(test_results_file, index_col=0)
        expected = pd.read_csv(join(datadir,'Simple_test_results.csv'), index_col=0)
        assert_frame_equal(actual, expected, check_dtype=False)

    def test_full_example_with_timezone(self):
        data_file = join(simpleexampledir,'simple.xlsx')
        df = pd.read_excel(data_file)
        df.index = df.index.tz_localize('MST')
        
        (QCI, test_results_file) = simple_example_run_analysis(df)
        
        """
   System Name          Variable Name                 Start Date                   End Date Timesteps                       Error Flag
1                                      2015-01-01 19:30:00-07:00  2015-01-01 19:30:00-07:00         1           Nonmonotonic timestamp
2                                      2015-01-01 17:00:00-07:00  2015-01-01 17:00:00-07:00         1              Duplicate timestamp
3                                      2015-01-01 05:00:00-07:00  2015-01-01 05:00:00-07:00         1                Missing timestamp
4               Wave Absolute Error C  2015-01-01 13:00:00-07:00  2015-01-01 14:45:00-07:00         8         Data > upper bound, 0.25
5       Simple                      A  2015-01-01 12:15:00-07:00  2015-01-01 14:30:00-07:00        10  Increment < lower bound, 0.0001
6       Simple                      B  2015-01-01 06:30:00-07:00  2015-01-01 06:30:00-07:00         1            Data < lower bound, 0
7       Simple                      B  2015-01-01 15:30:00-07:00  2015-01-01 15:30:00-07:00         1            Data > upper bound, 1
8       Simple                      C  2015-01-01 07:30:00-07:00  2015-01-01 09:30:00-07:00         9                     Corrupt data
9       Simple                      C  2015-01-01 13:00:00-07:00  2015-01-01 13:00:00-07:00         1     Increment > upper bound, 0.6
10      Simple                      D  2015-01-01 17:45:00-07:00  2015-01-01 18:15:00-07:00         3                     Missing data
11      Simple                      D  2015-01-01 11:15:00-07:00  2015-01-01 11:15:00-07:00         1           Data < lower bound, -1
12      Simple                      D  2015-01-01 12:45:00-07:00  2015-01-01 12:45:00-07:00         1           Data < lower bound, -1
13      Simple                      D  2015-01-01 03:15:00-07:00  2015-01-01 03:30:00-07:00         2            Data > upper bound, 1
14      Simple                      D  2015-01-01 04:00:00-07:00  2015-01-01 04:00:00-07:00         1            Data > upper bound, 1
15      Simple                      D  2015-01-01 04:30:00-07:00  2015-01-01 04:45:00-07:00         2            Data > upper bound, 1
16      Simple                      D  2015-01-01 18:30:00-07:00  2015-01-01 18:45:00-07:00         2            Data > upper bound, 1
17      Simple                      D  2015-01-01 19:15:00-07:00  2015-01-01 19:45:00-07:00         3            Data > upper bound, 1
"""
        assert_almost_equal(QCI.iloc[0,0],0.871227,6)
        
        actual = pd.read_csv(test_results_file, index_col=0)
        expected = pd.read_csv(join(datadir,'Simple_test_results_with_timezone.csv'), index_col=0)
        assert_frame_equal(actual, expected, check_dtype=False)

class Test_get_time(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.nPeriods = 48
        index = pd.date_range('1/1/1990 2:15', periods=self.nPeriods, freq='H')
        data = np.random.rand(self.nPeriods)
        df = pd.DataFrame(data=data, index=index, columns=['test'])
        
        self.pm = pecos.monitoring.PerformanceMonitoring()
        self.pm.add_dataframe(df, 'Test')

    @classmethod
    def tearDown(self):
        pass
        
    def test_get_elapsed_time(self):
        elapsed_time = self.pm.get_elapsed_time()
        expected = np.arange(0,self.nPeriods*3600,3600)
        assert_list_equal(elapsed_time.iloc[:,0].values.tolist(), expected.tolist())

    def test_get_clock_time(self):
        clock_time = self.pm.get_clock_time()
        expected = np.mod(np.arange(2.25*3600,(self.nPeriods+2.25)*3600,3600), 86400)
        assert_list_equal(clock_time.iloc[:,0].values.tolist(), expected.tolist())
    
    def test_get_elapsed_time_with_timezone(self):
        self.pm.df.index = self.pm.df.index.tz_localize('MST')
        elapsed_time = self.pm.get_elapsed_time()
        expected = np.arange(0,self.nPeriods*3600,3600)
        assert_list_equal(elapsed_time.iloc[:,0].values.tolist(), expected.tolist())
        
    def test_get_clock_time_with_timezone(self):
        self.pm.df.index = self.pm.df.index.tz_localize('MST')
        clock_time = self.pm.get_clock_time()
        expected = np.mod(np.arange(2.25*3600,(self.nPeriods+2.25)*3600,3600), 86400)
        assert_list_equal(clock_time.iloc[:,0].values.tolist(), expected.tolist())
