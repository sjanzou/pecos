import pecos
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
from os.path import join, abspath
from glob import glob

systems = ['system1', 'system2', 'system3']
locations = ['location1', 'location2']
analysis_date = datetime.date.today()-datetime.timedelta(days=1)
    
def dashboard_driver():
    for system in systems:
        for location in locations:
            try: 
                create_report(system, location, analysis_date)
            except: 
                pass
    
    create_dashboard(systems, analysis_date)

def create_report(system_name, location_name, analysis_date):
    
    # Input
    config_file = system_name + '_config.yml'
    
    # Open config file and extract information
    fid = open(config_file, 'r')
    config = yaml.load(fid)
    fid.close()
    trans = config['Translation']
    specs = config['Specifications']
    range_bounds = config['Range Bounds']

    # Create an PerformanceMonitoring instance
    pm = pecos.PerformanceMonitoring()
    
    # Populate the PerformanceMonitoring instance (with fake data)
    index = pd.date_range(analysis_date, periods=24, freq='H')
    data=np.sin(np.random.rand(3,1)*np.arange(0,24,1))
    df = pd.DataFrame(data=data.transpose(), index=index, columns=['A', 'B', 'C'])
    pm.add_dataframe(df, system_name)
    pm.add_translation_dictonary(trans, system_name)
    
    # Set options to create results directories
    pm.options.results_directory = 'Results'
    pm.options.results_subdirectory_root = location_name + '_' + system_name
    pm.options.results_subdirectory_prefix = analysis_date.strftime('_%Y_%m_%d')
    pm.options.make_results_directory()
    pm.options.make_results_subdirectory()
    
    # Check timestamp
    pm.check_timestamp(specs['Frequency']) 
    
    # Generate time filter
    clock_time = pm.get_clock_time()
    time_filter = (clock_time > specs['Time Filter Min']*3600) & (clock_time < specs['Time Filter Max']*3600)
    pm.add_time_filter(time_filter)
    
    # Check missing
    pm.check_missing()
    
    # Check range
    for key,value in range_bounds.items():
        pm.check_range(value, key) 
    
    # Compute metrics
    QCI = pm.compute_QCI()
    
    # Create a custom graphic
    df.plot()
    plt.savefig(os.path.join(pm.options.results_subdirectory, system_name + '_custom.jpg')) 
    
    # Generate report
    pm.write_test_results_file()
    pm.write_performance_metric_file(QCI)
    pm.write_HTML_report(config)

def create_dashboard(systems, analysis_date):
    
    results_directory = 'Results'
    prefix = analysis_date.strftime('%Y_%m_%d')
    
    dash = pecos.Dashboard()
    content = pd.DataFrame(index=systems, columns=locations)
    for location in content.columns:
        for system in content.index:
            root = location + '_' + system

            custom_graphic_files = glob(abspath(join(results_directory, root + '_' + prefix, '*custom*.jpg')))
            
            content.loc[system, location] = {
                'href': abspath(join(results_directory, root + '_' + prefix, root + '.html')),
                'images': custom_graphic_files}
    
    dash.write_HTML_dashboard(prefix, content)
    
if __name__ == '__main__':
    dashboard_driver()