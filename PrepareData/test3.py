import numpy as np
from Utils.Utils import get_mongo_connection, read_users, chunkIt
from Utils.Filepath import USERS, HISTORICAL_COLLECTION, HIS_FREQS, TWEETS_COLLECTION
import time
import pandas as pd
from collections import defaultdict
import datetime

import matplotlib.pyplot as plt


import pickle as pk
if __name__ =="__main__":
    user = pk.load(open("data/nodes.p","rb"))
    date = []
    for i in user.values():
        date.append(i)
    dat = pd.DataFrame(date)
    freqs = dat.groupby([dat[0].dt.year,dat[0].dt.month,dat[0].dt.day]).count()
    print(freqs)
    print(freqs.columns)
    #plt.hist(freqs)
    #plt.hist(date)
    #plt.plot(freqs,kind="bar")
    freqs = freqs.rename(columns={0:"Freqs"})
    freqs.iloc[200:].plot(kind="bar")
    print(datetime.date(2016,9,1))
    #plt.xlim([10,40])
    print(freqs.shape)
    plt.show()