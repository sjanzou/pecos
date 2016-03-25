import numpy as np
import logging
from nose.plugins.skip import SkipTest

logger = logging.getLogger(__name__)

@SkipTest
def write_test_results(filename, test_results):
    """
    Write test results file
    
    Parameters
    -----------
    filename : string
        Filename with full path
    
    test_results : pd.DataFrame
        Test results stored in pm.test_results
    """
    
    test_results.sort_values(['System Name', 'Variable Name'], inplace=True)
    test_results.index = np.arange(1, test_results.shape[0]+1)
    
    logger.info("Writing test results csv file " + filename)
    
    fout = open(filename, 'w')
    test_results.to_csv(fout, na_rep = 'NaN')
    fout.close()
