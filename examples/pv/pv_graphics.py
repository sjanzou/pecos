import matplotlib.pyplot as plt
from pecos.graphics import plot_timeseries, plot_scatter
import os

def graphics(filename_root, pm):
    
    filename_root = os.path.abspath(filename_root)
    
    # Colect file names
    custom_graphics = []
    
    # Plot DC Power over time
    plt.figure(figsize = (5.0,2.5))
    try:
        plotdata = pm.df[pm.trans['DC Power']]
    except:
        plotdata = None
    plot_timeseries(plotdata, pm.tfilter, yaxis_min=-200)
    plt.legend(['String 1', 'String 2'], fontsize=8) 
    plt.ylabel('DC Power', fontsize=8)
    filename = filename_root + '1.png'
    custom_graphics.append(filename)
    plt.savefig(filename, format='png', dpi=1000)
    plt.close()  
    
    # Plot Irradiance over time
    plt.figure(figsize = (5.0,2.5))
    try:
        irr_columns = pm.trans['GHI']
        irr_columns.extend(pm.trans['DHI'])
        irr_columns.extend(pm.trans['DNI'])
        plotdata = pm.df[irr_columns]
    except:
        plotdata = None
    plot_timeseries(plotdata, pm.tfilter, yaxis_min=-200, yaxis_max=1200)
    plt.legend(['GHI', 'DHI', 'DNI'], fontsize=8) 
    plt.ylabel('Irradiance', fontsize=8) 
    filename = filename_root + '2.png'
    custom_graphics.append(filename)
    plt.savefig(filename, format='png', dpi=1000)
    plt.close()  
    
    # Plot DC Power vs POA
    plt.figure(figsize = (5.0,2.5))
    try:
        plotdata_x = pm.df[pm.trans['POA']][pm.tfilter]
        plotdata_y = pm.df[pm.trans['DC Power']][pm.tfilter]
        if plotdata.isnull().all().all():
            plotdata_x = None
            plotdata_y = None
    except:
        plotdata_x = None
        plotdata_y = None
    plot_scatter(plotdata_x,plotdata_y, yaxis_min=-200)
    plt.legend(['String 1', 'String 2'], fontsize=8, loc='lower right')
    plt.xlabel('POA', fontsize=8)
    plt.ylabel('DC Power', fontsize=8)
    filename = filename_root + '3.png'
    custom_graphics.append(filename)
    plt.savefig(filename, format='png', dpi=1000)
    plt.close()  
    
    # Plot normalized efficiency
    plt.figure(figsize = (5.0,2.5))
    try:
        plotdata = pm.df[pm.trans['Normalized Efficiency']]
    except:
        plotdata = None
    plot_timeseries(plotdata, pm.tfilter) 
    plt.ylabel('Normalized Efficiency', fontsize=8) 
    filename = filename_root + '4.png'
    custom_graphics.append(filename)
    plt.savefig(filename, format='png', dpi=1000)
    plt.close()  
    
    # Plot DC Power actual vs. expected
    plt.figure(figsize = (5.0,2.5))
    try:
        plotdata_x = pm.df[pm.trans['Expected DC Power']][pm.tfilter]/2 # divided by 2 strings
        plotdata_y = pm.df[pm.trans['DC Power']][pm.tfilter]
        if plotdata.isnull().all().all():
            plotdata_x = None
            plotdata_y = None
    except:
        plotdata_x = None
        plotdata_y = None
    plot_scatter(plotdata_x,plotdata_y, yaxis_min=-200)
    plt.legend(['String 1', 'String 2'], fontsize=8, loc='lower right')
    plt.xlabel('Expected DC Power', fontsize=8)
    plt.ylabel('DC Power', fontsize=8)
    filename = filename_root + '5.png'
    custom_graphics.append(filename)
    plt.savefig(filename, format='png', dpi=1000)
    plt.close()  
    
    return custom_graphics
