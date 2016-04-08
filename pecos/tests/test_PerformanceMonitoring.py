from nose.tools import *
from os.path import abspath, dirname, join
import pecos
import datetime

testdir = dirname(abspath(__file__))
datadir = join(testdir,'data')

trans = {
'Range': ['Range1', 'Range2'],
'Deviation': ['Deviation1'],
'Corrupt': ['Corrupt1'],
'Missing': ['Missing1', 'Missing2'],
'All': ['Range1', 'Range2', 'Deviation1', 'Corrupt1', 'Missing1', 'Missing2'],
'Composite': ['(R1-sum(M))/R1', '(R2-sum(M))/R2', 'M1*D^2', 'M2*D^2', 'mean(All)-10']}

composite_signals = [
{'Comp1 (R-sum(M))/R': 'np.divide(({Range} - {Missing}.sum(axis=1)),{Range})'},
{'Comp2 M*D^2': '{Missing}*np.power({Deviation},2)'},
{'Comp3 mean(ALL)-10': '({All}).mean(axis=1) - 10'}]

file_date = [datetime.datetime(2014, 1, 1, 0, 0, 0)]

def test_check_timestamp():
    system_name = 'TEST_db1'
    file_name = join(datadir,'TEST_db1_2014_01_01.dat')
    df = pecos.io.read_campbell_scientific(file_name, 'TIMESTAMP')
    pm = pecos.monitoring.PerformanceMonitoring()
    pm.add_dataframe(df, system_name)
    pm.add_translation_dictonary(trans, system_name)

    pm.check_timestamp(3600) # 1 hour data
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
    assert_equal(sum(pm.test_results['Error Flag'] == 'Nonmonotonic timestamp'), 3)
    assert_equal(sum(pm.test_results['Error Flag'] == 'Duplicate timestamp'), 3)
    assert_equal(sum(pm.test_results['Error Flag'] == 'Missing timestamp'), 2)
    assert_equal(sum(pm.test_results['Timesteps']), 12)

def test_check_missing():
    system_name = 'TEST_db1'
    file_name = join(datadir,'TEST_db1_2014_01_01.dat')
    df = pecos.io.read_campbell_scientific(file_name, 'TIMESTAMP')
    pm = pecos.monitoring.PerformanceMonitoring()
    pm.add_dataframe(df, system_name)
    pm.add_translation_dictonary(trans, system_name)

    pm.check_missing()

    temp = pm.test_results[pm.test_results['Error Flag'] == 'Missing data']
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
    print(temp['Timesteps'])
    assert_items_equal(temp['Timesteps'], expected)

def test_check_corrupt():
    system_name = 'TEST_db1'
    file_name = join(datadir,'TEST_db1_2014_01_01.dat')
    df = pecos.io.read_campbell_scientific(file_name, 'TIMESTAMP')
    pm = pecos.monitoring.PerformanceMonitoring()
    pm.add_dataframe(df, system_name)
    pm.add_translation_dictonary(trans, system_name)

    pm.check_timestamp(3600)
    pm.check_corrupt([-999])

    temp = pm.test_results[pm.test_results['Error Flag'] == 'Corrupt data']

    """
      System Name       Variable Name          Start Date            End Date Timesteps    Error Flag
0              TEST_db1:Corrupt1 2014-01-01 11:00:00 2014-01-01 11:00:00         1  Corrupt Data
1              TEST_db1:Corrupt1 2014-01-02 09:00:00 2014-01-02 10:00:00         2  Corrupt Data
    """
    expected = [1,2]
    assert_items_equal(temp['Timesteps'], expected)

def test_check_range():
    system_name = 'TEST_db1'
    file_name = join(datadir,'TEST_db1_2014_01_01.dat')
    df = pecos.io.read_campbell_scientific(file_name, 'TIMESTAMP')
    pm = pecos.monitoring.PerformanceMonitoring()
    pm.add_dataframe(df, system_name)
    pm.add_translation_dictonary(trans, system_name)

    pm.check_range([1,3],'Range')

    assert_equal(pm.test_results.shape[0], 6)
    assert_equal(sum(pm.test_results['Timesteps']), 11)
    assert_equal(set(pm.test_results['Variable Name']), set(['Range1', 'Range2']))

#def test_composite_signal():
#    system_name = 'TEST_db1'
#    file_name = join(datadir,'TEST_db1_2014_01_01.dat')
#    df = pecos.io.read_campbell_scientific(file_name, 'TIMESTAMP')
#    pm = pecos.monitoring.PerformanceMonitoring()
#    pm.add_dataframe(df, system_name)
#    pm.add_translation_dictonary(trans, system_name)
#
#    pm.check_corrupt([-999])
#
#    for composite_signal in composite_signals:
#        for key,value in composite_signal.items():
#            signal = pm.evaluate_string(key, value)
#            pm.add_signal(key, signal)
#
#    error = max(pm.df['TEST_db1:(R1-sum(M))/R1'] - pm.df['Comp1 (R-sum(M))/R 1'])
#    assert_greater(0.01, error)
#    error = max(pm.df['TEST_db1:(R2-sum(M))/R2'] - pm.df['Comp1 (R-sum(M))/R 2'])
#    assert_greater(0.01, error)
#    error = max(pm.df['TEST_db1:M1*D^2'] - pm.df['Comp2 M*D^2 1'])
#    assert_greater(0.01, error)
#    error = max(pm.df['TEST_db1:M2*D^2'] - pm.df['Comp2 M*D^2 2'])
#    assert_greater(0.01, error)
#    error = max(pm.df['TEST_db1:mean(All)-10'] - pm.df['Comp3 mean(ALL)-10'])
#    assert_greater(0.01, error)

if __name__ == '__main__':
    #test_check_timestamp()
    #test_check_missing()
    #test_check_corrupt()
    #test_check_deviation()
    #test_check_range()
    test_composite_signal()
