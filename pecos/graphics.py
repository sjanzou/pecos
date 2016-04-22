"""
The graphics module contains functions to format scatter and time series 
plots for reporting.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import textwrap
import logging

try:
    from nose.tools import nottest
except ImportError:
    def nottest(afunction):
        return afunction
        
logger = logging.getLogger(__name__)

def plot_scatter(x,y,xaxis_min=None, xaxis_max=None, yaxis_min=None, yaxis_max=None):
    """
    Create a scatter plot
    
    Parameters
    ----------
    x : pd.Series
        x data
    
    y : pd.Series
        y data
    
    xaxis_min : float (optional)
        X-axis minimum        
        
    xaxis_max : float (optional)
        X-axis maximum    
        
    yaxis_min : float (optional)
        Y-axis minimum            
        
    yaxis_max : float (optional)
        Y-axis maximum         
    """
    
    ax = plt.gca()

    try:
        if x.shape[1] == y.shape[1]:
            for i in range(x.shape[1]):
                plt.plot(x.iloc[:,i],y.iloc[:,i], '.', markersize=3) #, color=next(colors))
                plt.xticks(rotation='vertical')
                plt.hold(True)
        elif x.shape[1] != y.shape[1]:
            if x.shape[1] == 1:
                for col in y.columns:
                    plt.plot(x,y[col], '.', markersize=3) #, color=next(colors))
                    plt.xticks(rotation='vertical')
                    plt.hold(True)
            elif y.shape[1] == 1:
                for col in x.columns:
                    plt.plot(x[col],y, '.', markersize=3) #, color=next(colors))
                    plt.xticks(rotation='vertical')
                    plt.hold(True)
    except:
        plt.text(0.3,0.5,'Insufficient Data', fontsize=8)
    
    # Format axis
    xmin_plt, xmax_plt = plt.xlim()
    ymin_plt, ymax_plt = plt.ylim()
    if not xaxis_min:
        xaxis_min = xmin_plt
    if not xaxis_max:
        xaxis_max = xmax_plt
    if not yaxis_min:
        yaxis_min = ymin_plt
    if not yaxis_max:
        yaxis_max = ymax_plt
    plt.ylim((xaxis_min, xaxis_max))
    plt.ylim((yaxis_min, yaxis_max))
    ax.tick_params(axis='both', labelsize=8)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0+0.2, box.width, box.height*0.8])
    
def plot_timeseries(data, tfilter, test_results_group=None, xaxis_min=None, xaxis_max=None, yaxis_min=None, yaxis_max=None):
    """
    Create a timeseries plot
    
    Parameters
    ----------
    data : pd.Series
        Data, indexed by time
        
    tfilter : pd.Series
        Boolean values used to include time filter in the plot 
        
    test_results_group : pd.Series (optional)
        Test results grouped by variable name
    
    xaxis_min : float (optional)
        X-axis minimum        
        
    xaxis_max : float (optional)
        X-axis maximum    
        
    yaxis_min : float (optional)
        Y-axis minimum            
        
    yaxis_max : float (optional)
        Y-axis maximum   
    """
    
    ax = plt.gca()
    
    try:
        # plot timeseries
        if isinstance(data, pd.Series):
            data.plot(ax=ax, grid=False, legend=False, color='k', fontsize=8, rot=90, label='Data', x_compat=True)
        else:
            data.plot(ax=ax, grid=False, legend=False, fontsize=8, rot=90, label='Data')
    
        # add tfilter        
        temp = np.where(tfilter - tfilter.shift())
        temp = np.append(temp[0],len(tfilter)-1)
        count = 0
        for i in range(len(temp)-1):
            if tfilter[temp[i]] == 0:
                if count == 0:
                    ax.axvspan(data.index[temp[i]], data.index[temp[i+1]], facecolor='k', alpha=0.2, label='Time filter')
                    count = count+1
                else:
                    ax.axvspan(data.index[temp[i]], data.index[temp[i+1]], facecolor='k', alpha=0.2)     
        
        # add errors 
        try:
            if test_results_group.empty:
                test_results_group = None
        except:
            pass
        if test_results_group is not None:
            key2 = test_results_group['Error Flag']
            grouped2 = test_results_group.groupby(key2)
            
            for error_flag in key2.unique():
                test_results_group2 = grouped2.get_group(error_flag)
                
                error_label = '\n'.join(textwrap.wrap(error_flag, 30))
                warning_label = '\n'.join(textwrap.wrap('Warning ' + str(test_results_group2.index.values).strip('[]'), 30)) #str(out_df2.index.values).strip('[]'), 30))
                error_label = error_label + '\n' + warning_label
                
                date_idx2 = np.array([False]*len(data.index))
                for row2 in range(len(test_results_group2.index)):
                    date_idx2 = date_idx2 + ((data.index >= test_results_group2.iloc[row2,2]) & (data.index <= test_results_group2.iloc[row2,3]))
                
                if sum(date_idx2) == 0:
                    continue
                
                data2 = data[date_idx2]
                if error_flag in ['Duplicate timestamp', 'Missing data', 'Corrupt data', 'Nonmonotonic timestamp']:
                    continue
                if "Data <" in error_flag:
                    try:
                        ax.scatter(data2.index, data2.values, c='r', marker='+', label=error_label)   
                    except:
                        ax.scatter(data2.index[0], data2.values[0], c='r', marker='+', label=error_label) 
                elif "Data >" in error_flag:
                    try:
                        ax.scatter(data2.index, data2.values, c='r', marker='+', label=error_label) 
                    except:
                        ax.scatter(data2.index[0], data2.values[0], c='r', marker='+', label=error_label) 
                else:
                    try:
                        ax.scatter(data2.index, data2.values, c='g', marker='+', label=error_label)  
                    except:
                        ax.scatter(data2.index[0], data2.values[0], c='g', marker='+', label=error_label) 
        
        # Format axis
        xmin_plt, xmax_plt = plt.xlim()
        ymin_plt = np.nanmin(data[tfilter].values)
        ymax_plt = np.nanmax(data[tfilter].values)
        if np.abs(ymin_plt - ymax_plt) < 0.01:
            ymin_plt, ymax_plt = plt.ylim()
    except:
        plt.text(0.3,0.5,'Insufficient Data', fontsize=8)
        xmin_plt, xmax_plt = plt.xlim()
        ymin_plt, ymax_plt = plt.ylim()
    
    # Format axis
    y_range = (ymax_plt - ymin_plt)
    if not xaxis_min:
        xaxis_min = xmin_plt
    if not xaxis_max:
        xaxis_max = xmax_plt
    if not yaxis_min:
        yaxis_min = ymin_plt-y_range/10
    if not yaxis_max:
        yaxis_max = ymax_plt+y_range/10
    plt.ylim((xaxis_min, xaxis_max))
    plt.ylim((yaxis_min, yaxis_max))
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.tick_params(axis='both', labelsize=8)
    plt.xlabel('Time', fontsize=8)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0+0.2, box.width, box.height*0.64])

@nottest
def plot_test_results(filename, pm):
    """
    Create test results graphics.
    Graphics include data that failed a quality control test.

    Parameters
    ----------
    filename : string
        Filename root, each graphic is appended with '_pecos_*.jpg' where * is an integer

    pm : PerformanceMonitoring object
        Contains data (pm.df) and test results (pm.test_results)
    """
    if pm.test_results.empty:
        return

    graphic = 0

    tfilter = pm.tfilter

    grouped = pm.test_results.groupby(['System Name', 'Variable Name'])

    for name, test_results_group in grouped:
        if name[1] == ' ':
            continue
        elif name[0] == '':
            col_name = str(name[1])
        else:
            col_name = str(name[0]) + ":" + str(name[1])


        if test_results_group['Error Flag'].all() in ['Duplicate timestamp', 'Missing data', 'Corrupt data', 'Missing timestamp', 'Nonmonotonic timestamp']:
            continue
        logger.info("Creating graphic for " + col_name)
        plt.figure(figsize = (7.0,2.5))
        plot_timeseries(pm.df[col_name], tfilter, test_results_group = test_results_group)

        ax = plt.gca()
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*0.65, box.height])
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
        plt.title(col_name, fontsize=8)

        plt.savefig(filename +'_pecos_'+str(graphic)+'.jpg', format='jpg', dpi=500)
        graphic = graphic + 1
        plt.close()
