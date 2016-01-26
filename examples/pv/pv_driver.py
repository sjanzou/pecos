import pecos
import datetime
import yaml
import pv_application
from glob import glob
import os

# Input
system_name = 'Baseline_System'
analysis_dates = [datetime.date(2015, 11, 11)]
config_file = 'Baseline_config.yml'

# Open config file and extract information
fid = open(config_file, 'r')
config = yaml.load(fid)
fid.close()
general = config['General'] 
trans = config['Translation']
specs = config['Specifications']
composite_signals = config['Composite Signals']
corrupt_values = config['Corrupt Values']
range_bounds = config['Range Bounds']
increment_bounds = config['Increment Bounds']

# Create an PerformanceMonitoring instance
pm = pecos.PerformanceMonitoring()

# Populate the PerformanceMonitoring instance
for db_name in trans.keys():
    for analysis_date in analysis_dates:
        analysis_date = analysis_date.strftime(general['Date Format'])
        db_files = glob(os.path.join(general['File Directory'], db_name + analysis_date + '*'))
        for db_file in db_files:
            df = pecos.read_campbell_scientific_file(db_file, general['Index Column'], encoding='utf-16')
            pm.add_dataframe(df, db_name)
    pm.add_translation_dictonary(trans[db_name], db_name)
    
# Set options to create result directories
pm.options.results_directory = 'Results'
pm.options.results_subdirectory_root = system_name
pm.options.results_subdirectory_prefix = '_'+ str(analysis_dates[0])
pm.options.make_results_directory()
pm.options.make_results_subdirectory()
pm.options.clean_results_subdirectory()

# Check timestamp
pm.check_timestamp(specs['Frequency']) 
    
# Generate time filter
time_filter = pv_application.calculate_time_filter(pm.df.index, specs)  
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
    pm.check_range(value, key, specs) 

# Check increment
for key,value in increment_bounds.items():
    pm.check_increment([value[0], value[1]], key, specs, min_failures=value[2]) 
    
# Compute metrics
QCI = pm.compute_QCI()
pv_metrics = pv_application.metrics(pm)
metrics = QCI.join(pv_metrics)

# Generate custom graphics
pv_application.graphics(pm)

# Generate report
pm.write_performance_metric_file(metrics)
pm.write_test_results_file()
pm.write_HTML_report(config)

    
