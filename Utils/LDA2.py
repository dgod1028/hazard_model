##
# Author : Li Yinxing ( Tohoku University )

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
import gensim.parsing.preprocessing as pre

#### Must
PATH = ('C:/users/Administrator/Documents/TwitterProject')      # Change to your path here
HIS_FILE = "iPhone8_comment.csv"                     # path of text file



#### Optional   *path for if save tmp files
LDA_FILE = "tmp/his_lda.lda"
DICT_FILE = "tmp/his_lda.dict"
CORP_FILE = "tmp/his_lda.mm"
USER_TOPIC_FILE = "tmp/his_user_topic.pkl"
USER_IDS_FILE = "tmp/his_user_ids.pkl"
TEXT_FILE = "tmp/his_text.pkl"
UTEXT_FILE = "tmp/his_utext.pkl"

os.chdir(PATH)

class LDA:
    def __init__(self,t=10,multi=True,debug=False,savetmp = False):
        self.t = t
        self.multi = multi
        self.debug = debug
        self.save = savetmp
            
    ## Function for multiprocessing

    def todict(self,arg):
        return [arg["user_id"], arg["text"]]

    def LDA(self,file, type="p", by_user=False, update=True,col = 0):
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
                dat = self.read_file(file, type,col=col)
                if self.multi:
                    p = Pool()
                    utexts = defaultdict()
                    if type != "csv":   ## if JSON or Pickle file
                        tmp = p.map(self.todict, dat)  ### return [user_id,text] for each user
                        texts = []
                        ### Aggregate texts by users.
                        for i in tmp:
                            if utexts.get(str(i[0])) == None:
                                utexts[str(i[0])] = []
                            ### Text Cleaning
                            cleaned_text = i[1].split(" ")
                            utexts[str(i[0])].append(cleaned_text)
                            # print(cleaned_text)
                            texts.append(cleaned_text)
                    else:
                        ### Clean Text
                        stoplist = set('for a of the and to in 0 1 2 3 4 5 6 7 8 9'.split())  ## add any other stopwords
                        texts = [[word for word in document.lower().split() if word not in stoplist] for document in dat]  ##  lower, split
                        #print(texts)
                    p.close()
                else:
                    texts = []
                    utexts = []
                    for i in dat:
                        texts.append(i["text"])
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
                print("Run LDA...",end="")
            #print(common_corpus)
            lda = LdaModel(common_corpus,id2word=common_dictionary, num_topics=self.t)
            lda.save(LDA_FILE)
            if self.debug:
                print("Finished!")
            return [lda,common_corpus,common_dictionary]
        else:
            model = self.load_topic(LDA_FILE)
            corpus = MmCorpus(CORP_FILE)
            dictionary = Dictionary.load(DICT_FILE)
            return [model, corpus, dictionary]
    def load_topic(self,file):
        return LdaModel.load(file)
    def doctopic2vec(self, doc_topic):
        ## Doctopic for each Document (For Multiprocessing)
        ## doc_topic -> [(0, 0.3), (2, 0.6)]. If Topic Number = 3 then convert to [0.3, 0, 0.6]
        mat = np.zeros(self.t)
        for i in doc_topic:
            mat[i[0]] = i[1]
        return mat
    def doctopic2mat(self,doc_topics,path = ""):
        """

        :param doc_topics: Document topics extracted by get_document_topics function from LDA model
        :param path      : 1. Save topic_share to path if self.savetmp == True.  2. If topic share file exists at path,
                            then skip create again, load file from path instead.
        :return          : pandas Dataframe Topic share.
        """
        if path == "" or os.path.isfile(path)==False:
            ### Create Topic share matrix for each document
            if self.multi:
                p = Pool()
                mat = p.map(self.doctopic2vec,doc_topics)
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
                topic_share.to_csv(path,index=False)
            return pd.DataFrame(nmat)
        else:
            return pd.read_csv(path)
    def get_user_id(self,text):
        return text["user_id"]
    def get_user_ids(self,file,path=""):
        self.save_allert(path)
        if path!="":
            if os.path.isfile(path):
                return pk.load(open(path,"rb"))
        dat = pk.load(open(file,"rb"))
        if self.multi:
            p = Pool()
            id = p.map(self.get_user_id,dat)
        else:
            id = []
            for i in dat:
                id.append(self.get_user_id(i))
        if self.save:
            pk.dump(id,open(path,"wb"))

        return id
    """  ## Maybe memoryoff if data is too big.
    def unique_ids(self,ids):
        u_ids = []
        for id in ids:
            if id not in u_ids:
                u_ids.append(id)
        return u_ids
    """
    def user_topics(self,doc_topics,ids,path=""):
        self.save_allert(path)
        if path!= "":
            if os.path.isfile(path):
                return pk.load(open(path,"rb"))
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
        if self.save:
            pk.dump(user_topics,open(path,"wb"))
        return user_topics
    def topical_similarity(self,user1,user2):
        #return cosine_similarity(user1,user2)  ## Error
        return 1-cosine(user1,user2)

    def normalization(self,vec):
        s = np.sum(vec)
        if s == 0:
            return vec
        else:
            for i in range(len(vec)):
                vec[i] /= s
            return vec
    def save_allert(self,path):
        if self.save:
            assert path!="", 'Please input path for save tmp file.'
    def read_file(self,file, type='p',encoding='utf-8',col=0):
        """

        :param file: file path
        :param type: JSON or p or csv
        :param encoding: default utf-8
        :param col:  if csv, define text column number (0, 1, 2 ... )
        :return: text list
        """
        if type == 'p':
            return pk.load(open(file, "rb"))
        elif type == 'json':
            return js.load(open(file,'rb'))
        elif type == 'csv':
            return pd.read_csv(file,encoding=encoding).iloc[:,col]


if __name__ == "__main__":
    # 1. Run LDA Model
    lda = LDA(t=4,multi=True,debug=True,savetmp=True)
    model,corpus,dic = lda.LDA(file=HIS_FILE,update=True,type='csv',col=1)

    # 2. Get Topic share for each documents
    dt = model.get_document_topics(corpus)

    # 各トピックごとの単語の抽出（topicsの引数を-1にすることで、ありったけのトピックを結果として返してくれます。）
    model.print_topics(num_topics=-1, num_words=230)


    # トピックごとの上位10語をCSVで出力
    print('Top words')
    topicdata = model.print_topics(num_topics=-1, num_words=20)
    print(topicdata)
    pd.DataFrame(topicdata).to_csv("topic_detail_lda.csv")

    """  For Twitter Data
    # 3. Get user ids for each documents    **example: get user id list --> dt[0] --> user_id 0   dt[1] --> user_id 5
    user_ids = lda.get_user_ids(HIS_FILE, USER_IDS_FILE)

    # 4. Calculate Topic share for each users.
    user_topics = lda.user_topics(doc_topics=dt, ids= user_ids, path= USER_TOPIC_FILE)
    #for key in user_topics.keys():
    #   print("{0}\t\t:{1}".format(key,user_topics[key]) )
    #print(lda.topical_similarity(user_topics["40184043"],user_topics["2202380486"]))

    ## Example
    print(user_topics["341135120"])
    print(user_topics["1315351699"])
    print(lda.topical_similarity(user_topics["341135120"],user_topics["1315351699"]))
    
    topic_share = lda.doctopic2mat(dt,savefile=True,path="tmp/topic_share.csv")
    """

