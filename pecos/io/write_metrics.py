import pandas as pd
import logging

logger = logging.getLogger(__name__)

def write_metrics(filename, metrics):
    """
    Add metric to the stats file
    
    Parameters
    -----------
    stat : pd.Series
        Data to add to the stats file
    """
    logger.info("Write metrics file")

    try:
        previous_metrics = pd.read_csv(filename, index_col='TIMESTEP', parse_dates=True)
    except:
        previous_metrics = pd.DataFrame()
    
    metrics = metrics.combine_first(previous_metrics) 
    
    fout = open(filename, 'w')
    metrics.to_csv(fout, index_label='TIMESTEP', na_rep = 'NaN')
    fout.close()
