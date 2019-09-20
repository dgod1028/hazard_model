"""
Here I will add all initial file path

"""
import os
os.chdir("d:/github/hazard_model")

### Collections of Mongo DB
INTERACTION_COLLECTION = "Interactions"
#TWEETS_COLLECTION = 'Tweets'
#TWEETS_COLLECTION = 'ThisIsUs_o'
TWEETS_COLLECTION = {"ThisIsUs":['ThisIsUs_new','ThisIsUs_o'],
                     "24Legacy":["ThisIsUs_new","ThisIsUs_o","TheGoodPlace_new","TheGoodPlace_o"],
                     "TheGoodPlace":["TheGoodPlace_new","TheGoodPlace_o"]
                     }
HISTORICAL_COLLECTION = ['old_tweets','old_tweets_2017']

### Network-related
g = 'data/TheGoodPlace.graphml'
HIS_FREQS ='data/historical_frequencys.p'
INTERACTION_FILE = "data/Interactions.p"
DYNAMIC_NETWORK ="data/dg.p"


### Index
USERS = 'data/TheGoodPlace_users.p'
SPARSE_USER = "data/sparse_user2.p"           # <- User whose tweets frequency is lower than 10 in total.
JACCARD = "data/jaccard.p"
HUBS = "data/hubs.p"
SENTIMENT_DATA = "data/X4Tweets.json"
OFFICIAL = "data/official.p"
SENTIMENT = "data/Sentiment.p"


### LDA-related
USER_TOPICS = 'data/lda/user_topic_prob.p'    # User Topics Files from LDA Model
LDA_MODEL = 'data/lda/his_lda.lda'           # LDA model
LDA_TEXT = 'data/lda/his_text.p'             # Cleaned Text list using in LDA

