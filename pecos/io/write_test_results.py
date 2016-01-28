import numpy as np
import logging

logger = logging.getLogger(__name__)

def write_test_results(filename, test_results):
    test_results.sort(['System Name', 'Variable Name'], inplace=True)
    test_results.index = np.arange(1, test_results.shape[0]+1)
    
    logger.info("Writing test results csv file " + filename)
    
    fout = open(filename, 'w')
    test_results.to_csv(fout, na_rep = 'NaN')
    fout.close()
