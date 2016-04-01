"""
In this example, simple time series data is used to demonstrate basic functions
in pecos.  
* Data is loaded from an excel file which contains four columns of values that 
  follow linear, random, and sine models.
* A translation dictionary is defined to map and group the raw data into 
  common names for analysis
* A time filter is established to screen out data between 3 AM and9 PM
* The data is loaded into a pecos PerformanceMonitoring class and a series of 
  quality control tests are run, including range tests and increment tests 
* The results are printed to csv and html reports
"""
import pecos
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# Initialize logger
pecos.logger.initialize()

# Input
system_name = 'Simple'
data_file = 'simple.xlsx'
translation_dictonary = {
    'Linear': ['A'],
    'Random': ['B'],
    'Wave': ['C','D']}
expected_frequency = 900
time_filter_min = 3*3600
time_filter_max = 21*3600
corrupt_values = [-999]
range_bounds = {
    'Random': [0, 1],
    'Wave': [-1, 1],
    'Wave Absolute Error': [None, 0.25]}
increment_bounds = {
    'Linear': [0.0001, None],
    'Random': [0.0001, None],
    'Wave': [0.0001, 0.5]}
    
 # Define output files and directories
results_directory = 'Results'
if not os.path.exists(results_directory):
    os.makedirs(results_directory)
results_subdirectory = os.path.join(results_directory, system_name + '_2015_01_01')
if not os.path.exists(results_subdirectory):
    os.makedirs(results_subdirectory)
metrics_file = os.path.join(results_directory, system_name + '_metrics.csv')
test_results_file = os.path.join(results_subdirectory, system_name + '_test_results.csv')
report_file =  os.path.join(results_subdirectory, system_name + '.html')

# Create an PerformanceMonitoring instance
pm = pecos.monitoring.PerformanceMonitoring()

# Populate the PerformanceMonitoring instance
df = pd.read_excel(data_file)
pm.add_dataframe(df, system_name)
pm.add_translation_dictonary(translation_dictonary, system_name)

# Check timestamp
pm.check_timestamp(expected_frequency)
 
# Generate time filter
clock_time = pm.get_clock_time()
time_filter = (clock_time > time_filter_min) & (clock_time < time_filter_max)
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
wave_mode_abs_error = np.abs(np.subtract(pm.df[pm.trans['Wave']], wave_model))
wave_mode_abs_error.columns=['Wave Absolute Error C', 'Wave Absolute Error D']
pm.add_signal('Wave Absolute Error', wave_mode_abs_error)

# Check range
for key,value in range_bounds.items():
    pm.check_range(value, key)

# Check increment
for key,value in increment_bounds.items():
    pm.check_increment(value, key) 
    
# Compute metrics
mask = pm.get_test_results_mask()
QCI = pecos.metrics.qci(mask, pm.tfilter)
 
# Create a custom graphic
plt.figure(figsize = (7.0,3.5))
ax = plt.gca()
df.plot(ax=ax, ylim=[-1.5,1.5])
plt.savefig(os.path.join(results_subdirectory, system_name+'_custom_1.jpg')) 

# Write metrics, test results, and report files
pecos.io.write_metrics(metrics_file, QCI)
pecos.io.write_test_results(test_results_file, pm.test_results)
pecos.io.write_monitoring_report(report_file, results_subdirectory, pm, QCI)
