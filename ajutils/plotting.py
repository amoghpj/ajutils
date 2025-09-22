import seaborn as sns
def plot_defaults():
    """
    TODO expand to specify arguments explicitly
    """
    sns.set(style="ticks")

def plottuples(toplot, ax, c='k',lw=1.0,ls='-'):
    """Plots list of tuples
    :param toplot: contains 2d data to plot
    :type toplot: list 
    :param ax: axis object
    """
    X = []
    Y = []
    for x,y in toplot:
        X.append(x)
        Y.append(y)
    ax.plot(X,Y,c=c,ls=ls,lw=lw)
