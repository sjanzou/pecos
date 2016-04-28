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
* A performance model is computed using pvlib, additional quality control test
  is run to compare observed to predicted power output
* PV performance metrics are computed
* The results are printed to csv and html reports
"""
import pecos
import datetime
import yaml
import os
import pandas as pd
import numpy as np
import pvlib
import pv_graphics

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
location = config['Location']
sapm_parameters = config['SAPM Parameters']
MET_translation_dictionary = config['MET Translation'] # translation dictionary for weather file
BASE_translation_dictionary = config['Baseline6kW Translation'] # translation dictionary for pv file
composite_signals = config['Composite Signals']
corrupt_values = config['Corrupt Values']
range_bounds = config['Range Bounds']
increment_bounds = config['Increment Bounds']

 # Define output files and directories
results_directory = 'Results'
if not os.path.exists(results_directory):
    os.makedirs(results_directory)
results_subdirectory = os.path.join(results_directory, system_name + '_'+ str(analysis_date))
if not os.path.exists(results_subdirectory):
    os.makedirs(results_subdirectory)
metrics_file = os.path.join(results_directory, system_name + '_metrics.csv')
test_results_file = os.path.join(results_subdirectory, system_name + '_test_results.csv')
report_file =  os.path.join(results_subdirectory, system_name + '.html')

# Create an PerformanceMonitoring instance
pm = pecos.monitoring.PerformanceMonitoring()

# Add pv system data
database_name = 'Baseline6kW'
database_file = database_name + analysis_date.strftime('_%Y_%m_%d') + '.dat'
df = pecos.io.read_campbell_scientific(database_file, 'TIMESTAMP', encoding='utf-16')
df.index = df.index.tz_localize(location['Timezone'])
pm.add_dataframe(df, database_name)
pm.add_translation_dictionary(BASE_translation_dictionary, database_name)
    
# Add weather data
database_name = 'MET'
database_file = database_name + analysis_date.strftime('_%Y_%m_%d') + '.dat'
df = pecos.io.read_campbell_scientific(database_file, 'TIMESTAMP', encoding='utf-16')
df.index = df.index.tz_localize(location['Timezone'])
pm.add_dataframe(df, database_name)
pm.add_translation_dictionary(MET_translation_dictionary, database_name)

# Check timestamp
pm.check_timestamp(60) 
    
# Generate time filter based on sun position
solarposition = pvlib.solarposition.ephemeris(pm.df.index, location['Latitude'], location['Longitude'])
time_filter = solarposition['apparent_elevation'] > 10 
pm.add_time_filter(time_filter)

# Check missing
pm.check_missing()

# Check corrupt
pm.check_corrupt(corrupt_values) 

# Add composite signals
for composite_signal in composite_signals:
    for key,value in composite_signal.items():
        signal = pm.evaluate_string(key, value)
        pm.add_signal(key, signal)

# Check range
for key,value in range_bounds.items():
    pm.check_range(value, key, sapm_parameters) 

# Check increment
for key,value in increment_bounds.items():
    pm.check_increment([value[0], value[1]], key, min_failures=value[2]) 
    
# Compute QCI
mask = pm.get_test_results_mask()
QCI = pecos.metrics.qci(mask, pm.tfilter)

# Generate a performance model using observed POA, wind speed, and air temp
# Remove data points that failed a previous qualtiy control test before
# running the model (using 'mask')
poa = pm.df[pm.trans['POA']][mask[pm.trans['POA']]]
wind = pm.df[pm.trans['Wind Speed']][mask[pm.trans['Wind Speed']]]
temp = pm.df[pm.trans['Ambient Temperature']][mask[pm.trans['Ambient Temperature']]]
sapm = pecos.pv.basic_pvlib_performance_model(sapm_parameters, 
                                              location['Latitude'], 
                                              location['Longitude'], 
                                              wind, temp, poa)

# Compute the relative error between observed and predicted DC Power.  
# Add the composite signal and run a range test
modeled_dcpower = sapm['p_mp']*sapm_parameters['Ns']*sapm_parameters['Np']
observed_dcpower = pm.df[pm.trans['DC Power']].sum(axis=1)
dc_power_relative_error = (np.abs(observed_dcpower - modeled_dcpower))/observed_dcpower
dc_power_relative_error = dc_power_relative_error.to_frame('DC Power Relative Error')
pm.add_signal('DC Power Relative Error', dc_power_relative_error)
pm.check_range([0,0.1], 'DC Power Relative Error') 

# Compute normalized efficiency, add the composite signal, and run a range test
P_ref = sapm_parameters['Vmpo']*sapm_parameters['Impo']*sapm_parameters['Ns']*sapm_parameters['Np'] # DC Power rating
NE = pecos.pv.normalized_efficiency(observed_dcpower, pm.df[pm.trans['POA']], P_ref)
pm.add_signal('Normalized Efficiency', NE)
pm.check_range([0.8, 1.2], 'Normalized Efficiency') 

# Compute energy
energy = pecos.pv.energy(pm.df[pm.trans['AC Power']], tfilter=pm.tfilter)
total_energy = energy.sum(axis=1).to_frame('Total Energy')

# Compute insolation
poa_insolation = pecos.pv.insolation(pm.df[pm.trans['POA']], tfilter=pm.tfilter)

# Compute performance ratio
PR = pecos.pv.performance_ratio(total_energy, poa_insolation, P_ref)

# Compute performance index
predicted_energy = pecos.pv.energy(modeled_dcpower, tfilter=pm.tfilter)
PI = pecos.pv.performance_index(total_energy, predicted_energy)

# Compute clearness index
dni_insolation = pecos.pv.insolation(pm.df[pm.trans['DNI']], tfilter=pm.tfilter)
ea = pvlib.irradiance.extraradiation(pm.df.index.dayofyear)
ea = pd.DataFrame(index=pm.df.index, data=ea, columns=['ea'])
ea_insolation = pecos.pv.insolation(ea, tfilter=pm.tfilter)
Kt = pecos.pv.clearness_index(dni_insolation, ea_insolation)

# Compute energy yield
energy_yield = pecos.pv.energy_yield(total_energy, P_ref)

# Collect metrics for reporting
total_energy = total_energy/3600/1000 # convert Ws to kWh
poa_insolation = poa_insolation/3600/1000 # convert Ws to kWh
energy_yield = energy_yield/3600 # convert s to h
total_energy.columns = ['Total Energy (kWh)']
poa_insolation.columns = ['POA Insolation (kWh/m2)']
energy_yield.columns = ['Energy Yield (kWh/kWp)']
metrics = pd.concat([QCI, PR, PI, Kt, total_energy, poa_insolation, energy_yield], axis=1)

# Generate custom graphics
filename = os.path.join(results_subdirectory, system_name)
pv_graphics.graphics(filename, pm)

# Generate reports
pecos.io.write_metrics(metrics_file, metrics)
pecos.io.write_test_results(test_results_file, pm.test_results)
pecos.io.write_monitoring_report(report_file, results_subdirectory, pm, metrics.transpose()), config)
