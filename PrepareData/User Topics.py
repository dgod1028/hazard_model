import argparse
import json as js
import numpy as np
import gzip
import os
import bson
import sys
#sys.path.append('/home/li/Hazard')
from collections import defaultdict

import pickle as pk
from time import time
import warnings

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.test.utils import common_texts
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
from gensim.corpora.mmcorpus import MmCorpus
from multiprocessing import Pool
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cosine
from Utils.Utils import get_mongo_connection,  divide_work
import gensim.parsing.preprocessing as pre
from Utils.Filepath_TheGoodPlace import HISTORICAL_COLLECTION,TWEETS_COLLECTION
import datetime
from PrepareData.LDA3 import preprocess_Tweets
from multiprocessing import Pool

CORE = 6
HIS = 1

LDA_FILE = "data/LDA/his_lda_6.lda"
lda = LdaModel.load(LDA_FILE)
db = get_mongo_connection()
#coll = db[HISTORICAL_COLLECTION[HIS]]
#coll = db[TWEETS_COLLECTION["TheGoodPlace"][HIS] ]
coll = db[TWEETS_COLLECTION["ThisIsUs"][HIS] ]
r = divide_work(coll.count(), CORE)


def config():
    parser = argparse.ArgumentParser(description="Inference User Topics")
    parser.add_argument('--o', type=int, help="Task ID (0 ~ Core number -1")
    return vars(parser.parse_args())

def clean_text(text):
    return text.split(" ")


def infer_topic(text):
    ctext = preprocess_Tweets([text])
    if len(ctext) > 0:
        bow = lda.id2word.doc2bow(ctext[0])
    else:
        bow = lda.id2word.doc2bow(ctext)
    tmp = lda.get_document_topics(bow)
    l = len(tmp)
    topics = np.zeros(l)
    for topic in tmp:
        topics[topic[0]] = topic[1]
    return topics


def user_topics(task=None):
    print("Start aggregate topics...")
    op = task
    rr = list(r[op])
    print("Process %i: from %i to %i" %(op, rr[0], rr[-1]+1))
    path = "TIU1_user_topics%s.p" % (op)
    dat = get_mongo_connection()
    #coll = dat[HISTORICAL_COLLECTION[HIS]]
    coll = db[TWEETS_COLLECTION["ThisIsUs"][HIS]]
    l = coll.count()
    users = defaultdict()
    count = 0
    for i in coll.find().skip(rr[0]).limit(rr[-1]-rr[0]):
        count += 1
        if count % 10000 == 0:
            time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            print("%s\tProgress: %i / %i" % (time, count, len(rr)))
        try:
            if i["user_id"] in users.keys():
                users[i["user_id"]] += infer_topic(i["text"])
            else:
                users[i["user_id"]] = infer_topic(i["text"])
        except:
            try:
                if i["user"]["id"] in users.keys():
                    users[i["user"]["id"]] += infer_topic(i["text"])
                else:
                    users[i["user"]["id"]] = infer_topic(i["text"])
            except:
                pass
    print("Start normalization...")
    count = 0
    #for key in users.keys():
    #    count += 1
    #    if count % 100 == 0:
    #        print("Progress: %i / %i" % (count, l))
    #    users[key] = normalization(users[key])
    if path != "":
        pk.dump(users, open(path, "wb"))
    return users

def normalization(vec):
    s = np.sum(vec)
    if s == 0:
        return vec
    else:
        for i in range(len(vec)):
            vec[i] /= s
        return vec

if __name__ == "__main__":
    #args = config()

    #op = sys.argv[1]
    #op = 7
    #rr = list(r[op])
    #print("Process %i: from %i to %i" %(op, rr[0], rr[-1]))
    #path = ["user_topics%s.p" % (op+8) for op in range(8)]
    #utopics = user_topics("user_topics%s.p" % op)
    with Pool() as p:
        utopics = p.map(user_topics, range(CORE))

    print("Finished")
    print(utopics)



