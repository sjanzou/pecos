"""
The metrics module contains performance metrics to track system health.
"""
import pandas as pd
import numpy as np
import datetime
import logging

logger = logging.getLogger(__name__)

def qci(mask, tfilter=None, per_day=True):
    """
    Quality control index (:math:`QCI`) is defined as:
    
    :math:`QCI=\dfrac{\sum_{d\in D}\sum_{t\in T}X_{dt}}{|DT|}`
    
    where 
    :math:`D` is the set of data columns and 
    :math:`T` is the set of time stamps in the analysis.  
    :math:`X_{dt}` is a data point for column :math:`d` time t` that passed all quality control test.  
    :math:`|DT|` is the number of data points in the analysis.
    
    Parameters
    ----------
    mask : pd.Dataframe
        Test results mask, returned from pm.get_test_results_mask()
    
    tfilter : Pandas Series (default = None)
        Time filter containing boolean values for each time index
        
    per_day : Boolean (default = True)
        Flag indicating if the results should be computed per day
    
    Returns
    -------
    QCI : pd.Series
        Quality control index
    """
    logger.info("Compute QCI")
    
    # Remove time filter
    if tfilter is not None:
        mask = mask[tfilter]
    
    if per_day:     
        dates = [mask.index[0].date() + datetime.timedelta(days=x) for x in range(0, (mask.index[-1].date()-mask.index[0].date()).days+1)]
    
        QCI = pd.DataFrame(index=pd.to_datetime(dates))
    
        for date in dates:
            mask_date = mask.loc[date.strftime('%m/%d/%Y')]
            try:
                QCIndex = mask_date.sum().sum()/float(mask_date.shape[0]*mask_date.shape[1])
                if np.isnan(QCIndex):
                    QCIndex = 0
                QCI.loc[date, 'Quality Control Index'] = QCIndex
            except:
                QCI.loc[date, 'Quality Control Index'] = 0
    else:
        QCI = mask.sum().sum()/float(mask.shape[0]*mask.shape[1])
        
    return QCI   

def time_integral(df, time_unit=1, tfilter=None, per_day=True):
    """
    Compute the time integral of each column in the dataframe.
    The time integral is computed using the trapezoidal rule from numpy.trapz.
    Results are given in [original data units]*seconds.
    
    Parameters
    -----------
    df : pd.DataFrame
        Data
        
    time_unit : float (default = 1)
        Convert time unit of integration.  time_unit = 3600 returns integral in units of hours.
         
    tfilter : pd.Series (default = None)
        Time filter containing boolean values for each time index
        
    per_day : Boolean (default = True)
        Flag indicating if the results should be computed per day
    
    Returns
    -------
    df_integral : pd.DataFrame or float
        Time integral of the dataframe, each column is named 'Time integral of ' + original column name.
    """
    if tfilter is not None:
        df = df[tfilter]
        
    def compute_integral(data):
        val = {}
        tdelta = ((data.index - data.index[0]).values)/1000000000 # convert ns to seconds
        for col in data.columns:
            val['Time integral of ' + col] = float(np.trapz(data.loc[:,col], tdelta))
        return val
        
    if per_day:
        dates = [df.index[0].date() + datetime.timedelta(days=x) for x in range(0, (df.index[-1].date()-df.index[0].date()).days+1)]
        df_integral = pd.DataFrame(index=pd.to_datetime(dates))
        for date in dates:
            df_date = df.loc[date.strftime('%m/%d/%Y')] 
            df_int = compute_integral(df_date)
            for col in df_int:
                df_integral.loc[date, col] = df_int[col]
    else:
        df_integral = compute_integral(df)
        df_integral = pd.DataFrame(df_integral, index=[0])
    
    df_integral = df_integral/time_unit
    
    return df_integral