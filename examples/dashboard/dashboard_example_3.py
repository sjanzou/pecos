"""
This example illustrates the use of Pandas Styling options to color code tables.  
The example contains no quality control analysis.
"""
import pecos
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import rgb2hex
import os

# Color value used in Pandas Styling
def color_value(val):
    
    nThresholds = 10
    colors=[(0.75, 0.15, 0.15), (1, 0.75, 0.15), (0.15, 0.75, 0.15)]
    cmap = LinearSegmentedColormap.from_list(name='custom', colors = colors, N=nThresholds)
    
    return_color = ''
    if np.isnan(val):
        return_color = 'background-color: gray'
    elif val > 1:
        return_color = 'background-color: gray'
    elif val < 0:
        return_color = 'background-color: gray'
    else:
        binned_value = int(np.floor(val*10))
        rgb_color = cmap(binned_value)[:3]
        hex_color =  rgb2hex(rgb_color)
        return_color = 'background-color: ' + hex_color
    
    return return_color

# Define system names, location names, and analysis date
nLocations = 4
nSystems = 5
locations = ['location' + str(i+1) for i in range(nLocations)]
systems = ['system' + str(i+1) for i in range(nSystems)]

dashboard_content = {} # Initialize the dashboard content dictionary
np.random.seed(500) # Set a random seed for metrics values

for location_name in locations:
    for system_name in systems:
        
        # Populate performance metrics (which would normally be computed based 
        # on data analysis)
        metrics = pd.DataFrame(data=np.random.rand(3), 
                               columns=[''],
                               index=['DA', 'QCI', 'EPI'])
        
        # Apply color and formatting to metrics table
        style_table = (
            metrics.style
            .format("{:.2f}")
            .applymap(color_value) 
            .highlight_null(null_color='gray')
            .render()
        )
        
        # Store content to be displayed in the dashboard
        content = {'table': style_table}
        dashboard_content[(location_name, system_name)] = content

# Create dashboard  
results_directory = 'Results_3'
if not os.path.exists(results_directory):
    os.makedirs(results_directory)
dashboard_filename = os.path.join(results_directory, 'Dashboard_example.html')  
footnote = 'DA = Data availability <br>QCI = Quality control index <br>EPI = Energy performance index'
pecos.io.write_dashboard(dashboard_filename, systems, locations, 
                         dashboard_content, footnote=footnote)
