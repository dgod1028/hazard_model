from matplotlib import pyplot as plt

def plot(data, show=True, ymin=None, xlabel=None, ylabel=None, main = "plot.png"):
    for k,d in data.items():
        plt.plot(d, label=k)
    plt.legend()
    if ymin != None:
        plt.ylim(ymin=ymin)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    if show:
        plt.show()
    else:
        plt.savefig(main)
    plt.clf()

def hist(data, show=True, ymin=None):
    for k,d in data.items():
        plt.hist(d, label=k)
    plt.legend()
    if ymin != None:
        plt.ylim(ymin=ymin)
    if show:
        plt.show()
    else:
        plt.savefig("plot.png")
    plt.clf()

def plot_distrubtion(data, num_plots, show=True):
    fig = plt.figure(figsize=(25, 20))
    row, col = 4, 4
    assert num_plots <= row * col
    for i in range(1, num_plots+1):
        plt.subplot(row, col, i)
        plt.hist(data[i-1], label="Step {}".format(i))
        plt.legend()
    fig.suptitle("Hazard rate distribution by step")
    if show:
        plt.show()
    else:
        plt.savefig("plot_dist.png")
    plt.clf()