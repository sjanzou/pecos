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

 # Define output files and directories
results_directory = 'Results'
if not os.path.exists(results_directory):
    os.makedirs(results_directory)
results_subdirectory = os.path.join(results_directory, system_name + '_'+analysis_date)
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
pm.add_translation_dictonary(trans, system_name)

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
plt.savefig(os.path.join(results_subdirectory, system_name+'_custom_1.jpg')) 

# Generate report
pecos.io.write_test_results(test_results_file, pm.test_results)
pecos.io.write_monitoring_report(report_file, results_subdirectory, pm, config=config)
