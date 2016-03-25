import matplotlib.pyplot as plt
from pecos.graphics import plot_timeseries
import logging
from nose.plugins.skip import SkipTest

logger = logging.getLogger(__name__)

@SkipTest
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
        