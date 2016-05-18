"""
This example is the same as simple_example.py, but it uses a configuration 
file to define the quality control analysis input.
"""
import pecos
import pandas as pd
import matplotlib.pyplot as plt
import os
import yaml

# Initialize logger
pecos.logger.initialize()

# Input
system_name = 'Simple'
analysis_date = '1_1_2015'
data_file = 'simple.xlsx'
config_file = 'simple_config.yml'
  
# Open config file and extract information
fid = open(config_file, 'r')
config = yaml.load(fid)
fid.close()
specs = config['Specifications']
translation_dictionary = config['Translation']
composite_signals = config['Composite Signals']
time_filter = config['Time Filter']
corrupt_values = config['Corrupt Values']
range_bounds = config['Range Bounds']
increment_bounds = config['Increment Bounds']
   
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
pm.add_translation_dictionary(translation_dictionary, system_name)

# Check timestamp
pm.check_timestamp(specs['Frequency'])
 
# Generate time filter
time_filter = pm.evaluate_string('Time Filter', time_filter)
pm.add_time_filter(time_filter)

# Check missing
pm.check_missing()
        
# Check corrupt
pm.check_corrupt(corrupt_values) 

# Add composite signals
for composite_signal in composite_signals:
    for key, value in composite_signal.items():
        signal = pm.evaluate_string(key, value, specs)
        pm.add_signal(key, signal)

# Check range
for key,value in range_bounds.items():
    pm.check_range(value, key)

# Check increment
for key,value in increment_bounds.items():
    pm.check_increment(value, key) 
    
# Compute metrics
mask = pm.get_test_results_mask()
QCI = pecos.metrics.qci(mask, pm.tfilter)
 
# Generate graphics
test_results_filename_root = os.path.join(results_subdirectory, 'test_results')
test_results_graphics = pecos.graphics.plot_test_results(test_results_filename_root, pm)
plt.figure(figsize = (7.0,3.5))
ax = plt.gca()
df.plot(ax=ax, ylim=[-1.5,1.5])
custom_graphic = os.path.abspath(os.path.join(results_subdirectory, 'custom.png'))
plt.savefig(custom_graphic, format='png', dpi=500)

# Write metrics, test results, and report files
pecos.io.write_metrics(metrics_file, QCI)
pecos.io.write_test_results(test_results_file, pm.test_results)
pecos.io.write_monitoring_report(report_file, pm, test_results_graphics, [custom_graphic], QCI)
