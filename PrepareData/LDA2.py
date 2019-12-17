##
##

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

#### Must
PATH = ('D:/Github/hazard_model')  # Change to your path here
HIS_FILE = "data/old_tweets_2017.p"  # path of historical tweets
TWEET_FILE = 'data/tweets.p'         # add for build LDA model with bos tweets and historical file
ALL_FILES = [HIS_FILE]

#### Optional   *path for if save tmp files
## Note that need to make directory tmp to save files in default
LDA_FILE = "data/LDA/his_lda.lda"
DICT_FILE = "data/LDA/his_lda.dict"
CORP_FILE = "data/LDA/his_lda.mm"
USER_TOPIC_FILE = "data/LDA/his_user_topic.p"
USER_IDS_FILE = "data/LDA/his_user_ids.p"
TEXT_FILE = "data/LDA/his_text.p"
UTEXT_FILE = "data/LDA/his_utext.p"

os.chdir(PATH)


class LDA:
    def __init__(self, t=10, multi=True, debug=False, savetmp=True):
        self.t = t
        self.multi = multi
        self.debug = debug
        self.save = savetmp

    ## Function for multiprocessing

    def todict(self,arg):  ## For his
        print("###")
        return [arg["user_id"], arg["text"]]


    def todict2(self,arg):
            return [arg["user"]["id"],arg["text"]]
    def todict3(self,arg):
        dat = get_mongo_connection()
        coll = dat[HISTORICAL_COLLECTION]
        dic = []
        l = len(list(arg))
        print("Total: %i" % l)
        count = 0
        for i in coll.find()[arg[0]:arg[-1]]:
            count += 1
            if count % 10000 == 0:
                print("Finished  %i / %i" %(count, l))
            dic.append([i['user_id'],i['text']])
        return dic

    def LDA(self, file, type="p", by_user=False, update=True):
        sta = time()

        """
        --- Input
        file   : historical data (json or pickle or csv)
        type   : pickle or json file type
        update : still run LDA even previous model file exists (will overwrite) 
                 * if file not exists, run LDA even update = False

        --- Output
        [LDA Model, corpus, dictionary]
        """
        if (os.path.isfile(LDA_FILE) and update == False) == False:  ### Check if already Done
            if (os.path.isfile(TEXT_FILE) and os.path.isfile(
                    UTEXT_FILE) and update == False) == False:
                ## If text list is not created, then create text list from pickle(or json)
                #dat = self.read_file(file[0], type) ## his data
                #dat2 = self.read_file(file[1],type) ## tweets data
                #dat = get_mongo_connection()
                #coll = dat[HISTORICAL_COLLECTION]
                if self.multi:
                    p = Pool(4)
                    utexts = defaultdict()  ## ignore all for utexts
                    print("Start collect text data")
                    #n = coll.count()
                    n = 10000
                    r = divide_work(n,4)
                    print(r)
                    s1 = time()
                    dat = get_mongo_connection()
                    coll = dat[HISTORICAL_COLLECTION]
                    coll.reindex()
                    doc =  coll.find()
                    print("Start Multi-processing...")
                    tmp = p.map(self.todict, doc[1:10000])  ### return [user_id,text] for each user
                    #tmp5 = []
                    #for i in tmp:
                    #    tmp5 += i

                    #tmp2 = p.map(self.todict2,dat2)
                    texts = []
                    ### Aggregate texts by users.
                    #tmp3 = tmp5
                    tmp3 = tmp
                    for i in tmp3:
                        if utexts.get(str(i[0])) == None:
                            utexts[str(i[0])] = []
                        ### Text Cleaning
                        """
                        Here put Text Cleaning
                        """
                        cleaned_text = i[1].split(" ")
                        utexts[str(i[0])].append(cleaned_text)
                        # print(cleaned_text)
                        texts.append(cleaned_text)
                    p.close()
                    print("Extract Cost\t: %.2f" %(time()-s1))
                #
                """ Need Fix for non multi
                else:
                    texts = []
                    utexts = []
                    for i in dat:
                        texts.append(i["text"])
                    for i in dat2:
                        texts.append(i["text"])
                """
                if self.debug:
                    print("Convert Cost\t: %.2f" % (time() - sta))
                pk.dump(texts, open(TEXT_FILE, "wb"))
                pk.dump(utexts, open(UTEXT_FILE, "wb"))

            else:  ### If text file is exists,
                if by_user:
                    pass
                    ### Add codes
                else:
                    texts = pk.load(open(TEXT_FILE, "rb"))
            # Create a corpus from a list of texts
            common_dictionary = Dictionary(texts)
            common_dictionary.save(DICT_FILE)
            common_corpus = [common_dictionary.doc2bow(text) for text in texts]
            MmCorpus.serialize(CORP_FILE, common_corpus)
            # Train the model on the corpus.
            if self.debug:
                print("Run LDA...", end="")
            lda = LdaModel(common_corpus, num_topics=self.t)
            lda.save(LDA_FILE)
            for user
            if self.debug:
                print("Finished!")
            return [lda, common_corpus, common_dictionary]
        else:
            model = self.load_topic(LDA_FILE)
            corpus = MmCorpus(CORP_FILE)
            dictionary = Dictionary.load(DICT_FILE)
            return [model, corpus, dictionary]

    def load_topic(self, file):
        return LdaModel.load(file)

    def doctopic2vec(self, doc_topic):
        ## Doctopic for each Document (For Multiprocessing)
        ## doc_topic -> [(0, 0.3), (2, 0.6)]. If Topic Number = 3 then convert to [0.3, 0, 0.6]
        mat = np.zeros(self.t)
        for i in doc_topic:
            mat[i[0]] = i[1]
        return mat

    def doctopic2mat(self, doc_topics, path=""):
        """

        :param doc_topics: Document topics extracted by get_document_topics function from LDA model
        :param path      : 1. Save topic_share to path if self.savetmp == True.  2. If topic share file exists at path,
                            then skip create again, load file from path instead.
        :return          : pandas Dataframe Topic share.
        """
        if path == "" or os.path.isfile(path) == False:
            ### Create Topic share matrix for each document
            if self.multi:
                p = Pool()
                mat = p.map(self.doctopic2vec, doc_topics)
                p.close()
            else:
                mat = []
                for i in doc_topics:
                    mat.append(self.doctopic2vec(i))
            nmat = np.asanyarray(mat)
            topic_share = pd.DataFrame(nmat)
            topic_share.columns = range(0, self.t)
            if self.save == True:
                assert path != None, 'Please input path!'
                topic_share.to_csv(path, index=False)
            return pd.DataFrame(nmat)
        else:
            return pd.read_csv(path)

    def get_user_id(self, text):
        return text["user_id"]

    def get_id(self,text):  ## for tweets
        return text["user"]["id"]

    def get_user_ids(self, file, path=""):
        self.save_allert(path)
        if path != "":
            if os.path.isfile(path):
                return pk.load(open(path, "rb"))
        #dat = pk.load(open(file[0], "rb"))
        coll = get_mongo_connection()[HISTORICAL_COLLECTION]
        #dat2 = pk.load(open(file[1], "rb"))
        if self.multi:
            p = Pool()
            id = p.map(self.get_user_id, coll.find()[:1000000])
            #id2 = p.map(self.get_id,dat2)
        else:
            id = []
            #id2 = []
            for i in dat:
                id.append(self.get_user_id(i))
            #for i in dat2:
             #   id2.append(self.get_id(i))
        if self.save:
            pk.dump(id, open(path, "wb"))

        return id

    """  ## Maybe memoryoff if data is too big.
    def unique_ids(self,ids):
        u_ids = []
        for id in ids:
            if id not in u_ids:
                u_ids.append(id)
        return u_ids
    """

    def user_topics(self, doc_topics, ids, path=""):
        self.save_allert(path)
        if path != "":
            if os.path.isfile(path):
                return pk.load(open(path, "rb"))
        user_topics = defaultdict()
        count = 0
        for doc in doc_topics:
            tmp = self.doctopic2vec(doc)
            id = str(ids[count])
            if user_topics.get(id) is None:
                user_topics[id] = tmp
            else:
                user_topics[id] += tmp
            count += 1
        ## Normalization
        for key in user_topics.keys():
            user_topics[key] = self.normalization(user_topics[key])
        pk.dump(user_topics, open(path, "wb"))
        return user_topics

    def topical_similarity(self, user1, user2):
        # return cosine_similarity(user1,user2)  ## Error
        return 1 - cosine(user1, user2)

    def normalization(self, vec):
        s = np.sum(vec)
        if s == 0:
            return vec
        else:
            for i in range(len(vec)):
                vec[i] /= s
            return vec

    def save_allert(self, path):
        if self.save:
            assert path != "", 'Please input path for save tmp file.'

    def read_file(self, file, type='p', encoding='utf-8'):
        if type == 'p':
            return pk.load(open(file, "rb"))
        elif type == 'json':
            return js.load(open(file, 'rb'))
        elif type == 'csv':
            return pd.read_csv(file, encoding=encoding)


if __name__ == "__main__":
    # 1. Run LDA Model
    lda = LDA(t=4, multi=True, debug=True, savetmp=True)
    model, corpus, dic = lda.LDA(file=ALL_FILES, update=True)

    # 2. Get Topic share for each documents
    dt = model.get_document_topics(corpus)
    # 3. Get user ids for each documents    **example: get user id list --> dt[0] --> user_id 0   dt[1] --> user_id 5
    user_ids = lda.get_user_ids(ALL_FILES, USER_IDS_FILE)

    # 4. Calculate Topic share for each users.
    user_topics = lda.user_topics(doc_topics=dt, ids=user_ids, path=USER_TOPIC_FILE)
    # for key in user_topics.keys():
    #   print("{0}\t\t:{1}".format(key,user_topics[key]) )
    # print(lda.topical_similarity(user_topics["40184043"],user_topics["2202380486"]))

    ## Example
    print(user_topics)
    print(user_topics["747976695618035712"])
    print(lda.topical_similarity(user_topics["2202380486"], user_topics["747976695618035712"]))
    """
    topic_share = lda.doctopic2mat(dt,savefile=True,path="tmp/topic_share.csv")
    """
    ### To Do
    ## Complete non multi
    ## Text Cleaning
    ## logging info
