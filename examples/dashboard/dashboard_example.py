"""
In this example, a dashboard is generated to view quality control analysis 
results using analysis from several systems and locations.  Each system and 
location links to a detailed report which includes test failures.
For illustrative purposes, the data used in this example is generated within 
the script, using a sine wave function.
"""
import pecos
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
from os.path import join, abspath
from glob import glob

# Initialize logger
pecos.logger.initialize()

systems = ['system1', 'system2', 'system3']
locations = ['location1', 'location2']
analysis_date = datetime.date.today()-datetime.timedelta(days=1)
results_directory = 'Results'
if not os.path.exists(results_directory):
    os.makedirs(results_directory)
dashboard_filename = os.path.join(results_directory, 'Dashboard_example.html')
dashboard_content = {} 

for location_name in locations:
    for system_name in systems:
        
        # Input
        config_file = system_name + '_config.yml'
        
        # Open config file and extract information
        fid = open(config_file, 'r')
        config = yaml.load(fid)
        fid.close()
        trans = config['Translation']
        specs = config['Specifications']
        range_bounds = config['Range Bounds']
    
        # Define output files and subdirectories
        location_system = location_name + '_' + system_name
        location_system_date = location_system + '_' + analysis_date.strftime('%Y_%m_%d')
        results_subdirectory = os.path.join(results_directory, location_system_date)
        if not os.path.exists(results_subdirectory):
            os.makedirs(results_subdirectory)
        metrics_file = os.path.join(results_directory, location_system + '_metrics.csv')
        test_results_file = os.path.join(results_subdirectory, location_system_date + '_test_results.csv')
        report_file =  os.path.join(results_subdirectory, location_system_date + '.html')
        
        
        # Create an PerformanceMonitoring instance
        pm = pecos.monitoring.PerformanceMonitoring()
        
        # Populate the PerformanceMonitoring instance (with fake data)
        index = pd.date_range(analysis_date, periods=24, freq='H')
        data=np.sin(np.random.rand(3,1)*np.arange(0,24,1))
        df = pd.DataFrame(data=data.transpose(), index=index, columns=['A', 'B', 'C'])
        pm.add_dataframe(df, system_name)
        pm.add_translation_dictonary(trans, system_name)

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
        mask = pm.get_test_results_mask()
        QCI = pecos.metrics.qci(mask, pm.tfilter)
        
        # Create a custom graphic
        df.plot()
        plt.savefig(os.path.join(results_subdirectory, location_system_date + '_custom.jpg')) 
        
        # Generate report
        pecos.io.write_test_results(test_results_file, pm.test_results)
        pecos.io.write_metrics(metrics_file, QCI)
        pecos.io.write_monitoring_report(report_file, results_subdirectory, pm)
            
        graphics = glob(abspath(join(results_subdirectory, '*custom*.jpg')))
        metrics_table = QCI.transpose().to_html(bold_rows=False, header=False)
        content = {'text': "Example text for " + location_system, 
                   'graphics': graphics, 
                   'table':  metrics_table, 
                   'link': abspath(report_file),
                   'link text': 'Link to Report'}
        dashboard_content[(system_name, location_name)] = content
        
pecos.io.write_dashboard(dashboard_filename, locations, systems, dashboard_content)
