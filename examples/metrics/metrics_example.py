"""
In this example, performance metrics from a pv system are analyzed to determine 
long term system health
* Daily performance metrics for 2016 are loaded from a csv file
* The files contain performance ratio and system availability.
* The metrics are loaded into a pecos PerformanceMonitoring 
  object and a series of quality control tests are run
* The results are printed to csv and html reports
"""
import pecos
import pandas as pd
import matplotlib.pyplot as plt
import os

# Initialize logger
pecos.logger.initialize()

# Input
system_name = 'System1'
analysis_date = '2016'
data_file = 'System1_2016_performance_metrics.xlsx'

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
translation_dictionary = dict(zip(df.columns, [[col] for col in df.columns])) # 1:1 translation
pm.add_translation_dictionary(translation_dictionary, system_name)

# Check timestamp
pm.check_timestamp(24*3600) 
        
# Check missing
pm.check_missing()
        
# Check corrupt
pm.check_corrupt([-999]) 

# Check range for all columns
for key in pm.trans.keys():
    pm.check_range([0,1], key)

# Check increment for all columns
for key in pm.trans.keys():
    pm.check_increment([-0.5, None], key, absolute_value=False) 
    
# Create a custom graphic
df.plot(ylim=[-0.2,1.2])
plt.savefig(os.path.join(results_subdirectory, system_name+'_custom_1.jpg')) 

# Generate report
pecos.io.write_test_results(test_results_file, pm.test_results)
pecos.io.write_monitoring_report(report_file, results_subdirectory, pm)
