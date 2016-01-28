import logging
import pandas as pd
import numpy as np
import datetime
import logging

logger = logging.getLogger(__name__)

def qci(pm):
    """
    Compute QC metric
    
    Parameters
    ----------
    add_metric : bool
        Add quality control index (QCI) to the stats file
        
    Returns
    -------
    qci : pd.Series
        Quality control index (QCI)
    """
    logger.info("Compute QCI")
    
    tfilter = pm.tfilter
    df = pm.df[tfilter]
    dates = [df.index[0].date() + datetime.timedelta(days=x) for x in range(0, (df.index[-1].date()-df.index[0].date()).days+1)]
    
    mask = pm.get_test_results_mask()
    mask = mask[tfilter]
            
    stats = pd.DataFrame(index=pd.to_datetime(dates))
    
    if mask.empty:
        for date in dates:
            stats.loc[date, 'Quality Control Index'] = 0
    else:
        for date in dates:
            mask_date = mask.loc[date.strftime('%m/%d/%Y')]
            
            # Quality Control Index
            QCIndex = mask_date.sum().sum()/float(mask_date.shape[0]*mask_date.shape[1])
            if np.isnan(QCIndex):
                QCIndex = 0
            stats.loc[date, 'Quality Control Index'] = QCIndex
    
    return stats   