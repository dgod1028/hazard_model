##
##

import json as js
import numpy as np
import gzip
import os
import bson
import sys
from collections import defaultdict
import logging
import pickle as pk
from time import time
import warnings
from string import punctuation

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.test.utils import common_texts
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
from gensim.models.ldamulticore import LdaMulticore
from gensim.corpora.mmcorpus import MmCorpus
from multiprocessing import Pool
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cosine
from Utils.Utils import get_mongo_connection,  divide_work
import gensim.parsing.preprocessing as pre
from Utils.Filepath import HISTORICAL_COLLECTION

from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
#import custom libraries
import re
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

#### Must
PATH = ('D:/Github/hazard_model')  # Change to your path here
HIS_FILE = "data/old_tweets_2017.p"  # path of historical tweets
TWEET_FILE = 'data/tweets.p'         # add for build LDA model with bos tweets and historical file
ALL_FILES = [HIS_FILE]

T = 5

tokenizer = TweetTokenizer(strip_handles=True, reduce_len=True)
lemmatizer = WordNetLemmatizer()

#### Optional   *path for if save tmp files
## Note that need to make directory tmp to save files in default
LDA_FILE = "data/LDA/his_lda_%i.lda" % T
DICT_FILE = "data/LDA/his_lda_%i.dict" % T
CORP_FILE = "data/LDA/his_lda_%i.mm" % T
USER_TOPIC_FILE = "data/LDA/his_user_topic.p"
USER_IDS_FILE = "data/LDA/his_user_ids.p"
TEXT_FILE = "data/LDA/his_text2.p"
UTEXT_FILE = "data/LDA/his_utext.p"
PERPLEXITY_FILE = "data/LDA/perplexity_%i.p" % T

os.chdir(PATH)

customWords = ['bc', 'http', 'https', 'co', 'com','rt', 'one', 'us', 'new',
              'lol', 'may', 'get', 'want', 'like', 'love', 'no', 'thank', 'would', 'thanks',
              'good', 'much', 'low', 'roger', 'im',"dont","fuck"]
alphabets = list(map(chr, range(97, 123)))
myStopWords = set(stopwords.words('english') + list(punctuation) + customWords + alphabets)


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
            if (os.path.isfile(TEXT_FILE) and update == False) == False:
                ## If text list is not created, then create text list from pickle(or json)
                if self.multi:
                    colls = HISTORICAL_COLLECTION + ["ThisIsUs_new","ThisIsUs_o","TheGoodPlace_new","TheGoodPlace_o"]
                    #p = Pool(8)
                    cleaned_texts = []
                    for colln in colls:
                        print("Start collect text data")
                        dat = get_mongo_connection()
                        coll = dat[colln]
                        n = coll.count()
                        core = 15
                        n = 1000000
                        r = divide_work(n,core)
                        #print(r)
                        s1 = time()

                        #coll.reindex()
                        #doc =  coll.find()
                        print("Start Multi-processing for %s..." %colln)
                        u = []
                        texts = []
                        excutor = ProcessPoolExecutor(core)
                        futures = []
                        for i in range(core):
                            futures.append( excutor.submit(self.get_text, r[i],colln ) )
                        for i in range(core):
                            texts += futures[i].result()
                        print(len(texts))
                        #for user in tqdm(doc[:1000000]):
                        #    #print(user)
                        #    try: u.append(user["user_id"])
                        #    except: u.append(user["user"]["id"])
                        #    ## Text Cleaning
                        #    texts.append(user["text"])

                        print("Start clean the text")
                        r2 = divide_work(len(texts),core)
                        futures = []
                        for i in range(core):
                            rr = list(r2[i])
                            futures.append( excutor.submit(preprocess_Tweets, texts[rr[1]:(rr[-1]+1)] ))

                        for i in range(len(futures)):
                            cleaned_texts += futures[i].result()

                if self.debug:
                    print("Convert Cost\t: %.2f" % (time() - sta))
                pk.dump(cleaned_texts, open(TEXT_FILE, "wb"))
                #pk.dump(utexts, open(UTEXT_FILE, "wb"))

            else:  ### If text file is exists,
                if by_user:
                    pass
                    ### Add codes
                else:
                    cleaned_texts = pk.load(open(TEXT_FILE, "rb"))
            # Create a corpus from a list of texts
            common_dictionary = Dictionary(cleaned_texts)
            common_dictionary.save(DICT_FILE)
            common_corpus = [common_dictionary.doc2bow(text) for text in cleaned_texts]
            MmCorpus.serialize(CORP_FILE, common_corpus)
            # Train the model on the corpus.
            if self.debug:
                print("Run LDA...", end="")
            #lda = LdaModel(common_corpus, num_topics=self.t,id2word=common_dictionary)
            lda = LdaMulticore(common_corpus, num_topics=self.t,id2word=common_dictionary,workers=10)
            self.lda = lda
            lda.save(LDA_FILE)
            log_perplexity = lda.log_perplexity(common_corpus)
            pk.dump(log_perplexity,open(PERPLEXITY_FILE,"wb"))
            if self.debug:
                print("Finished!")
            return [lda, common_corpus, common_dictionary]
        else:
            model = self.load_topic(LDA_FILE)
            self.lda = model
            corpus = MmCorpus(CORP_FILE)
            dictionary = Dictionary.load(DICT_FILE)
            return [model, corpus, dictionary]

    def load_topic(self, file):
        return LdaModel.load(file)

    def get_text(self,r,colln):
        rr = list(r)
        t =len(rr)
        dat = get_mongo_connection()
        coll = dat[colln]
        texts = []
        for user in tqdm(coll.find().skip(rr[0]).limit(rr[-1]-rr[0]+1), total=t):
            try:
                texts.append(user["text"])
            except:
                pass
        return texts

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
    def clean_text(self,text):
        return text.split(" ")
    def infer_topic(self,text):
        bow = self.lda.id2word.doc2bow(self.clean_text(text))
        tmp = self.lda.get_document_topics(bow)
        topics = np.zeros(self.t)
        for topic in tmp:
            topics[topic[0]] = topic[1]
        return topics
    def user_topics2(self,path=""):
        self.save_allert(path)
        if path != "":
            if os.path.isfile(path):
                return pk.load(open(path, "rb"))
        print("Start aggregate topics...")
        dat = get_mongo_connection()
        coll = dat[HISTORICAL_COLLECTION]
        l = coll.count()
        users = defaultdict()
        count = 0
        for i in coll.find():
            count += 1
            if count % 100 == 0:
                print("Progress: %i / %i" %(count, l))
            if i["user_id"] in users.keys():
                users[i["user_id"]] += self.infer_topic(i["text"])
            else:
                users[i["user_id"]] = self.infer_topic(i["text"])
        print("Start normalization...")
        count = 0
        for key in users.keys():
            count += 1
            if count % 100 == 0:
                print("Progress: %i / %i" %(count, l))
            users[key] = self.normalization(users[key])
        if path !="":
            pk.dump(users,open(path,"wb"))
        return users



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


def preprocess_Tweets(tweet_list: list) -> list:
    # Pre-process step 1 - Word Tokenization

    # 1. Word Tokenization
    words = list(tokenizer.tokenize(tweets) for tweets in tweet_list)
    logging.debug("--------> Tokenization complete...")

    # 2. Remove the stop words from the document
    words_steps2 = list()
    for tweet in words:
        sents = list(re.sub(r'\W+', '', word) for word in tweet)
        sents = filter(lambda s: not str(s).lstrip('-').isdigit(), sents)
        sents = list(word.lower() for word in sents if word not in myStopWords and word != '' and
                     not word.startswith('http'))
        if sents != None:
            words_steps2.append(sents)
    logging.debug("--------> Stop words removed...")

    # Pre-process step3 - Lemmatization
    pre_processed_list = list()
    for tweet in words_steps2:
        words_step4 = list()
        words_step3 = pos_tag(tweet)
        for token in words_step3:
            pos = get_wordnet_pos(token[1])
            # if verb, noun, adj or adverb include them after lemmatization
            if pos is not None and len(token[0]) > 3:
                try:
                    tok = lemmatizer.lemmatize(token[0], pos)
                    words_step4.append(tok)
                except UnicodeDecodeError:
                    pass
        if (words_step4 != [] and words_step4 != '\n'):
            #pre_processed_list.append(" ".join(words_step4))
            pre_processed_list.append(words_step4)
        else:
            continue
    logging.debug("--------> Lemmatization complete...")
    return pre_processed_list

def preprocess_Tweet(tweet_list: str) -> str:
    # Pre-process step 1 - Word Tokenization

    # 1. Word Tokenization
    words = list(tokenizer.tokenize(tweets) for tweets in tweet_list)
    logging.debug("--------> Tokenization complete...")

    # 2. Remove the stop words from the document
    words_steps2 = list()
    for tweet in words:
        sents = list(re.sub(r'\W+', '', word) for word in tweet)
        sents = filter(lambda s: not str(s).lstrip('-').isdigit(), sents)
        sents = list(word.lower() for word in sents if word not in myStopWords and word != '' and
                     not word.startswith('http'))
        if sents != None:
            words_steps2.append(sents)
    logging.debug("--------> Stop words removed...")

    # Pre-process step3 - Lemmatization
    pre_processed_list = list()
    for tweet in words_steps2:
        words_step4 = list()
        words_step3 = pos_tag(tweet)
        for token in words_step3:
            pos = get_wordnet_pos(token[1])
            # if verb, noun, adj or adverb include them after lemmatization
            if pos is not None and len(token[0]) > 3:
                try:
                    tok = lemmatizer.lemmatize(token[0], pos)
                    words_step4.append(tok)
                except UnicodeDecodeError:
                    pass
        if (words_step4 != [] and words_step4 != '\n'):
            #pre_processed_list.append(" ".join(words_step4))
            pre_processed_list.append(words_step4)
        else:
            continue
    logging.debug("--------> Lemmatization complete...")
    return pre_processed_list

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return 'a'
    elif treebank_tag.startswith('V'):
        return 'v'
    elif treebank_tag.startswith('N'):
        return 'n'
    elif treebank_tag.startswith('R'):
        return 'r'
    else:
        return None

if __name__ == "__main__":
    # 1. Run LDA Model
    lda = LDA(t=T, multi=True, debug=True, savetmp=True)
    model, corpus, dic = lda.LDA(file=ALL_FILES, update=False)

    # 2. Get Topic share for each documents
    #dt = model.get_document_topics(corpus)
    # 3. Get user ids for each documents    **example: get user id list --> dt[0] --> user_id 0   dt[1] --> user_id 5
    #user_ids = lda.get_user_ids(ALL_FILES, USER_IDS_FILE)

    # 4. Calculate Topic share for each users.
    #user_topics = lda.user_topics(doc_topics=dt, ids=user_ids, path=USER_TOPIC_FILE)
    #user_topics = lda.user_topics2(path=USER_TOPIC_FILE)
    # for key in user_topics.keys():
    #   print("{0}\t\t:{1}".format(key,user_topics[key]) )
    # print(lda.topical_similarity(user_topics["40184043"],user_topics["2202380486"]))

    ## Example
    #print(user_topics)
    #print(user_topics["747976695618035712"])
    #print(lda.topical_similarity(user_topics["2202380486"], user_topics["747976695618035712"]))
    """
    topic_share = lda.doctopic2mat(dt,savefile=True,path="tmp/topic_share.csv")
    """
    ### To Do
    ## Complete non multi
    ## Text Cleaning
    ## logging info
