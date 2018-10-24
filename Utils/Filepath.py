"""
Here I will add all initial file path

"""
import os
os.chdir("d:/github/hazard_model")

### Collections of Mongo DB
INTERACTION_COLLECTION = "Interactions"
TWEETS_COLLECTION = 'Tweets'
HISTORICAL_COLLECTION = 'old_tweets_2017'

### Network-related
g = 'data/ThisIsUS.graphml'
HIS_FREQS ='data/historical_frequencys.p'

### Index
USERS = 'data/users.p'


### LDA-related
USER_TOPICS = 'data/lda/his_user_topic.p'    # User Topics Files from LDA Model
LDA_MODEL = 'data/lda/his_lda.lda'           # LDA model
LDA_TEXT = 'data/lda/his_text.p'             # Cleaned Text list using in LDA
