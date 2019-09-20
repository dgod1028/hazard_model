
import json as js
import numpy as np
import gzip
import os
import bson
import sys
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
from Utils.Filepath import HISTORICAL_COLLECTION
import datetime
from PrepareData.LDA3 import preprocess_Tweets


LDA_FILE = "data/LDA/his_lda_20.lda"
lda = LdaModel.load(LDA_FILE)

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


def user_topics2(path=""):
    print("Start aggregate topics...")
    dat = get_mongo_connection()
    coll = dat[HISTORICAL_COLLECTION[0]]
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
    db = get_mongo_connection()
    coll = db[HISTORICAL_COLLECTION[0]]
    r = divide_work(coll.count(),8)
    #op = sys.argv[1]
    op = 7
    rr = list(r[op])
    print("Process %i: from %i to %i" %(op, rr[0], rr[-1]))
    user_topics = user_topics2("user_topics%s.p" % op)
    print("Finished")
    print(user_topics)



