import pecos
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import os

# Input
system_name = 'System1'
analysis_date = '2016'
config_file = 'System1_2016_config.yml'
data_file = 'System1_2016_performance_metrics.xlsx'

# Open config file and extract information
fid = open(config_file, 'r')
config = yaml.load(fid)
fid.close()
trans = config['Translation']
specs = config['Specifications']
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
pm.options.results_subdirectory_prefix = '_'+analysis_date
pm.options.make_results_directory()
pm.options.make_results_subdirectory()
pm.options.clean_results_subdirectory()

# Check timestamp
pm.check_timestamp(specs['Frequency']) 
        
# Check missing
pm.check_missing()
        
# Check corrupt
pm.check_corrupt(corrupt_values) 

# Check range
for key,value in range_bounds.items():
    pm.check_range(value, key)

# Check increment
for key,value in increment_bounds.items():
    pm.check_increment([value[0], value[1]], key, absolute_value=value[2]) 
    
# Create a custom graphic
df.plot(ylim=[-0.2,1.2])
plt.savefig(os.path.join(pm.options.results_subdirectory, system_name+'_custom_1.jpg')) 

# Generate report
pm.write_test_results_file()
pm.write_HTML_report(config)
