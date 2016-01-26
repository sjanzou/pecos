import pecos
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import os

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
trans = config['Translation']
composite_signals = config['Composite Signals']
time_filter = config['Time Filter']
corrupt_values = config['Corrupt Values']
range_bounds = config['Range Bounds']
increment_bounds = config['Increment Bounds']
    
# Create an PerformanceMonitoring instance
pm = pecos.PerformanceMonitoring()

# Populate the PerformanceMonitoring instance
df = pd.read_excel(data_file)
pm.add_dataframe(df, system_name)
pm.add_translation_dictonary(trans, system_name)

# Set options to create results directories
pm.options.results_directory = 'Results'
pm.options.results_subdirectory_root = system_name
pm.options.results_subdirectory_prefix = df.index.date[0].strftime('_%Y_%m_%d') + '_withconfig'
pm.options.make_results_directory()
pm.options.make_results_subdirectory()
pm.options.clean_results_subdirectory()

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
    for key,value in composite_signal.items():
        signal = pm.evaluate_string(key, value, specs)
        pm.add_signal(key, signal)

# Check range
for key,value in range_bounds.items():
    pm.check_range(value, key)

# Check increment
for key,value in increment_bounds.items():
    pm.check_increment(value, key) 
    
# Generate QC metrics
QCI = pm.compute_QCI()
    
# Create a custom graphic
df.plot(ylim=[-1.5,1.5])
plt.savefig(os.path.join(pm.options.results_subdirectory, system_name+'_custom_1.jpg')) 

# Generate report
pm.group_test_results()
pm.write_performance_metric_file(QCI)
pm.write_test_results_file()
pm.write_HTML_report(config)
