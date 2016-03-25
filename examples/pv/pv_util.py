import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pvlib
from pecos.graphics import plot_timeseries, plot_scatter

def graphics(filename, pm):
    
    data = pm.df
    trans = pm.trans
    tfilter = pm.tfilter
    
    # DC Power
    plt.figure(figsize = (5.0,2.5))
    try:
        plotdata = data[trans['DC Power']]
    except:
        plotdata = None
    plot_timeseries(plotdata, tfilter, yaxis_min=-200)
    plt.savefig(filename + '_custom1.jpg', format='jpg', dpi=1000)
    plt.close()  
    
    plt.figure(figsize = (5.0,2.5))
    try:
        plotdata_x = data[trans['POA']][tfilter]
        plotdata_y = data[trans['DC Power']][tfilter]
        if plotdata.isnull().all().all():
            plotdata_x = None
            plotdata_y = None
    except:
        plotdata_x = None
        plotdata_y = None
    plot_scatter(plotdata_x,plotdata_y, yaxis_min=-200)
    plt.xlabel('POA', fontsize=8)
    plt.ylabel('DC Power', fontsize=8)
    plt.savefig(filename + '_custom2.jpg', format='jpg', dpi=1000)
    plt.close()  
        
    # Plot irradiance
    plt.figure(figsize = (5.0,2.5))
    try:
        irr_columns = trans['GHI']
        irr_columns.extend(trans['DHI'])
        irr_columns.extend(trans['DNI'])
        plotdata = data[irr_columns]
    except:
        plotdata = None
    plot_timeseries(plotdata, tfilter, yaxis_min=-200, yaxis_max=1200)
    plt.legend(['GHI', 'DHI', 'DNI'], fontsize=8) 
    plt.ylabel('Irradiance', fontsize=8) 
    plt.savefig(filename +'_custom3.jpg', format='jpg', dpi=1000)
    plt.close()  
        
def metrics(pm):
    
    tfilter = pm.tfilter
    df = pm.df[tfilter]
    dates = [df.index[0].date() + datetime.timedelta(days=x) for x in range(0, (df.index[-1].date()-df.index[0].date()).days+1)]
    
    # remove data that signaled a warning
    mask = pm.get_test_results_mask()
    mask = mask[tfilter]
  
    stats = pd.DataFrame(index=pd.to_datetime(dates))
    
    #df = df[mask]
    
    for date in dates:
        df_date = df.loc[date.strftime('%m/%d/%Y')]
            
        # Clearness Index
        Ea = pvlib.irradiance.extraradiation(df_date.index.dayofyear)
        Ea = pd.DataFrame(index=df_date.index, data=Ea)
        dni = df_date[pm.trans['DNI']] # W/m2
        Ea = Ea[~dni.isnull().any(axis=1)]
        dni = dni[~dni.isnull().any(axis=1)]
        dnInsolation = np.sum(dni, axis=0)
        EaInsolation = np.sum(Ea, axis=0)
        CI = np.divide(dnInsolation, EaInsolation)
        stats.loc[date, 'Clearness Index'] = float(CI)
        
        #current = pm.df[pm.trans['DC Current']]
        #poa = pm.df[pm.trans['POA']]/1000
        #current_index = np.divide(np.mean(current, axis=0), np.mean(poa, axis=0))
        #stats.loc[date, 'Current Index'] = float(current_index)
        
    return stats
