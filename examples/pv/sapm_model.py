import pecos
import pvlib
import yaml
import os
import datetime
from glob import glob
import pandas as pd

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

 # Define output files and directories
results_directory = 'Results'
if not os.path.exists(results_directory):
    os.makedirs(results_directory)
results_subdirectory = os.path.join(results_directory, system_name + str(analysis_dates[0]))
if not os.path.exists(results_subdirectory):
    os.makedirs(results_subdirectory)
metrics_file = os.path.join(results_directory, system_name + '_metrics.csv')
test_results_file = os.path.join(results_subdirectory, system_name + '_test_results.csv')
report_file =  os.path.join(results_subdirectory, system_name + '.html')



# Create an PerformanceMonitoring instance
pm = pecos.monitoring.PerformanceMonitoring()

# Populate the PerformanceMonitoring instance
for db_name in trans.keys():
    for analysis_date in analysis_dates:
        analysis_date = analysis_date.strftime(general['Date Format'])
        db_files = glob(os.path.join(general['File Directory'], db_name + analysis_date + '*'))
        for db_file in db_files:
            df = pecos.io.read_campbell_scientific(db_file, general['Index Column'], encoding='utf-16')
            pm.add_dataframe(df, db_name)
    pm.add_translation_dictonary(trans[db_name], db_name)
    
# Check timestamp
pm.check_timestamp(specs['Frequency']) 

# Add composite signals
for composite_signal in composite_signals:
    for key,value in composite_signal.items():
        signal = pm.evaluate_string(key, value, specs)
        pm.add_signal(key, signal)

## SAPM
fid = open('Suniva_Optimus_270W_Black.yml', 'r')
module = yaml.load(fid)
fid.close()
module['#Series'] = module['Ns']

# Copute cell temperature
irrad = pm.df[pm.trans['POA']]
irrad = pd.Series(data = irrad.values[:,0], index = pm.df.index)
wind = pm.df[pm.trans['Wind Speed']]
wind = pd.Series(data = wind.values[:,0], index = pm.df.index)
temp = pm.df[pm.trans['Ambient Temperature']]
temp = pd.Series(data = temp.values[:,0], index = pm.df.index)
model = [module['a'], module['b'], module['deltaT']]
celltemp = pvlib.pvsystem.sapm_celltemp(irrad, wind, temp, model)

# Copute sun position
Location = pvlib.location.Location
Location.latitude = specs['Latitude']
Location.longitude = specs['Longitude']
Location.altitude = specs['Altitude']
Location.tz = specs['Timezone']
solarposition = pvlib.solarposition.ephemeris(pm.df.index, Location)
solarposition.index = solarposition.index.tz_localize(tz=None)

# Compute alsolute airmass
airmass_relative  = pvlib.atmosphere.relativeairmass(solarposition['zenith'], model='kastenyoung1989')
airmass_absolute = pvlib.atmosphere.absoluteairmass(airmass_relative, pressure=101325.0)

# Compute aoi
aoi = pvlib.irradiance.aoi(Location.latitude, 180, solarposition['zenith'], solarposition['azimuth'])

# Compute SAPM
poa_diffuse = pd.Series(data = 0, index = pm.df.index)
sapm_model = pvlib.pvsystem.sapm(module, irrad, poa_diffuse, celltemp['temp_cell'], airmass_absolute, aoi)
sapm_model.plot()

pm.df[pm.trans['DC Power']].plot()
sapm_model['p_mp'].plot()
