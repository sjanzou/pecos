"""
In this example, data from a 6KW PV system is used to demonstrate integration
between pecos and pvlib.  
* Time series data is loaded from two text files in Campbell Scientific format
* The files contain electrical output from the pv system and associated 
  weather data. 
* Translation dictionaries are defined to map and group the raw data into 
  common names for analysis
* A time filter is established based on sun position
* Electrical and weather data are loaded into a pecos PerformanceMonitoring 
  class and a series of quality control tests are run
* The results are printed to csv and html reports
"""
import pecos
import datetime
import yaml
import pv_graphics
import os
import pandas as pd
import pvlib

# Initialize logger
pecos.logger.initialize()

# Input
system_name = 'Baseline_System'
analysis_date = datetime.date(2015, 11, 11)
config_file = 'Baseline_config.yml'

# Open config file and extract information
fid = open(config_file, 'r')
config = yaml.load(fid)
fid.close()
general = config['General'] 
MET_translation_dictonary = config['MET Translation'] # translation dictonary for weather file
BASE_translation_dictonary = config['Baseline6kW Translation'] # translation dictonary for pv file
specs = config['Specifications']
composite_signals = config['Composite Signals']
corrupt_values = config['Corrupt Values']
range_bounds = config['Range Bounds']
increment_bounds = config['Increment Bounds']

 # Define output files and directories
results_directory = 'Results'
if not os.path.exists(results_directory):
    os.makedirs(results_directory)
results_subdirectory = os.path.join(results_directory, system_name + str(analysis_date))
if not os.path.exists(results_subdirectory):
    os.makedirs(results_subdirectory)
metrics_file = os.path.join(results_directory, system_name + '_metrics.csv')
test_results_file = os.path.join(results_subdirectory, system_name + '_test_results.csv')
report_file =  os.path.join(results_subdirectory, system_name + '.html')

# Create an PerformanceMonitoring instance
pm = pecos.monitoring.PerformanceMonitoring()

# Add pv system data
database_name = 'Baseline6kW'
database_file = database_name + analysis_date.strftime(general['Date Format']) + '.dat'
df = pecos.io.read_campbell_scientific(database_file, general['Index Column'], encoding='utf-16')
df.index = df.index.tz_localize(specs['Timezone'])
pm.add_dataframe(df, database_name)
pm.add_translation_dictonary(BASE_translation_dictonary, database_name)
    
# Add weather data
database_name = 'MET'
database_file = database_name + analysis_date.strftime(general['Date Format']) + '.dat'
df = pecos.io.read_campbell_scientific(database_file, general['Index Column'], encoding='utf-16')
df.index = df.index.tz_localize(specs['Timezone'])
pm.add_dataframe(df, database_name)
pm.add_translation_dictonary(MET_translation_dictonary, database_name)

# Check timestamp
pm.check_timestamp(specs['Frequency']) 
    
# Generate time filter based on sun position
solarposition = pvlib.solarposition.ephemeris(pm.df.index, specs['Latitude'], specs['Longitude'])
time_filter = solarposition['apparent_elevation'] > specs['Min Sun Elevation'] 
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
    
# Compute QCI
mask = pm.get_test_results_mask()
QCI = pecos.metrics.qci(mask, pm.tfilter)

# Compute performance ratio
poa_insolation = pecos.pv.insolation(pm.df[pm.trans['POA']], time_unit=3600, tfilter=pm.tfilter)
energy = pecos.pv.energy(pm.df[pm.trans['AC Power']], time_unit=3600, tfilter=pm.tfilter)
PR = pecos.pv.performance_ratio(energy.sum(axis=1), poa_insolation, specs['DC power rating'])

# Compute clearness index
dni_insolation = pecos.pv.time_integral(pm.df[pm.trans['POA']], time_unit=3600, tfilter=pm.tfilter)
ea = pvlib.irradiance.extraradiation(pm.df.index.dayofyear)
ea = pd.DataFrame(index=pm.df.index, data=ea, columns=['ea'])
ea_insolation = pecos.pv.time_integral(ea, time_unit=3600, tfilter=pm.tfilter)
Kt = pecos.pv.clearness_index(dni_insolation, ea_insolation)

metrics = pd.concat([QCI, PR, Kt], axis=1)

# Generate custom graphics
filename = os.path.join(results_subdirectory, system_name)
pv_graphics.graphics(filename, pm)

# Generate reports
pecos.io.write_metrics(metrics_file, metrics)
pecos.io.write_test_results(test_results_file, pm.test_results)
pecos.io.write_monitoring_report(report_file, results_subdirectory, pm, metrics, config)
    