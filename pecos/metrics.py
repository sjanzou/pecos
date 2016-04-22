import logging
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
    :math:`T` is the set of timestamps in the analysis.  
    :math:`X_{dt}` is a data point for column :math:`d` time t` that passed all quality control test.  
    :math:`|DT|` is the number of data points in the analysis.
    
    Parameters
    ----------
    mask : pd.Dataframe
        Test results mask, returned from pm.get_test_results_mask()
    
    tfilter : Pandas Series (default = None)
        Time filter containing boolean values for each time index
        
    per_day : Boolean (default = True)
        Flag indicating if the results shoudl be computed per day
    
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
