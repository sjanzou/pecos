import matplotlib.pyplot as plt
import logging

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
    