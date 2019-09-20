import json as js
import numpy as np
import gzip
import os
import bson
import sys
from collections import defaultdict
from tqdm import tqdm


import pickle as pk
from time import time
import warnings

def normalization(vec):
    s = np.sum(vec)
    if s == 0:
        return vec
    else:
        for i in range(len(vec)):
            vec[i] /= s
        return vec

def combine(topic_list,normalize=False):
    for i,t in tqdm(enumerate(topic_list)):
        if i == 0:
            user_topic = pk.load(open(t,"rb"))
        else:
            tmp = pk.load(open(t,"rb"))
            for k,v in tmp.items():
                try:
                    if k in user_topic.keys():
                        user_topic[k] += v
                    else:
                        user_topic[k] = v
                except:
                    print(i)
                    print(k)
                    print(v)
                    pass
    if normalize == True:
        count = 0
        for key in tqdm(user_topic.keys()):
            count += 1
           #if count % 100 == 0:
               #print("Progress: %i / %i" % (count, l))
            user_topic[key] = normalization(user_topic[key])

    return user_topic


if __name__ == "__main__":
    topiclist = ["../data/LDA/user_topics%i.p" % i for i in range(16)]
    user_topic = combine(topiclist)
    pk.dump(user_topic, open("user_topic.p", "wb"))
    user_topic = combine(topiclist,normalize=True)
    pk.dump(user_topic,open("user_topic_prob.p","wb"))
    print(user_topic)
    print(topiclist)
    #combine()
