import numpy as np
from Utils.Utils import get_mongo_connection, read_users, chunkIt, divide_work
from Utils.Filepath import USERS, HISTORICAL_COLLECTION, HIS_FREQS, TWEETS_COLLECTION
import time
import pandas as pd
from collections import defaultdict
import datetime
from multiprocessing import Pool
import sys


def query(range):
    db = get_mongo_connection()
    r = list(range[0])
    collf = db[HISTORICAL_COLLECTION].find()[r[0]:r[-1]]
    count = 0
    for i in collf:
        count +=1
        if count % 100000 == 0:
            print("No. %i Process: %i / %i" %(range[1], count, len(r)))

if __name__ =="__main__":
    p = Pool(processes=8)
    db = get_mongo_connection()
    l = db[HISTORICAL_COLLECTION].count()
    r = divide_work(l,8)
    rr = []
    for i in range(len(r)):
        rr.append([r[i],i+2])
    p.map(query,rr)