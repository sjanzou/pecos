import pandas as pd
import logging

logger = logging.getLogger(__name__)

def read_campbell_scientific(file_name, index_col='TIMESTAMP', encoding=None):
    """
    Read Campbell Scientific CSV file

    Parameters
    ----------
    file_name : string
        File name with full path

    index_col : string
        Index column name

    encoding : string
        character encoding (i.e. utf-16)
    """
    logger.info("Reading Campbell Scientific CSV file " + file_name)

    try:
        df = pd.read_csv(file_name, skiprows=1, encoding=encoding, index_col=index_col, parse_dates=True, dtype=unicode) #, low_memory=False)
        df = df[2:]
        index = pd.to_datetime(df.index)
        Unnamed = df.filter(regex='Unnamed')
        df = df.drop(Unnamed.columns, 1)
        df = pd.DataFrame(data = df.values, index = index, columns = df.columns, dtype='float64')
    except:
        logger.warning("Cannot extract database, CSV file reader failed " + file_name)
        df = pd.DataFrame()
        return

    # Drop rows with NaT (not a time) in the index
    try:
        df.drop(pd.NaT, inplace=True)
    except:
        pass

    return df
