from pymongo import MongoClient
import logging
from TvshowTweets.Tweet import *
import json

class TVshowTweets:
    # Data structure
    # {
    #   "userid": {
    #     "Timestamp1":    "SentimentValue1",
    #     "Timestamp2":    "SentimentValue2"
    #   }
    # }
    #
    # Output two json file:
    # tvshow_tweet.json contain all tweets have tv show's hashtag
    # historical_tweet.json contain all histrical tweets posted by the author in tvshow_tweet.json

    def __init__(self):
        logging.basicConfig(filename='Tweet_text.log', level=logging.INFO, format='%(asctime)s %(message)s')
        self.tvshow_tweets = {}
        self.historical_tweets = {}
        self.db = MongoClient()['stream_store']

    def add_tweet(self, userid, text, create_time, network):
        assert isinstance(userid, int), "User id must be int!"
        if userid not in network:
            network[userid] = {}
        network[userid][create_time] = text

    def add_show(self, show_name):
        assert show_name != '', "Hashtag shouldn't be empty!"

        # Added tweets have tv show's hashtag
        query_string = {"entities.hashtags.text": show_name}
        logging.info('\nQuery Tweets Begin\nQuery string is ' + str(query_string))
        for t in self.db.old_tweets_2017.find(query_string):
            tweet = Tweet(t)
            self.add_tweet(tweet.author_id, tweet.text, tweet.create_time, self.tvshow_tweets)
        tweet_users = len(self.tvshow_tweets.keys())
        logging.info('Analysis tweets with hashtag {} finished. {} users added.'.format(show_name, tweet_users))

        # Look at historical tweets from each twitter author
        count = 0
        for user_id in self.tvshow_tweets.keys():
            query_string = {"user.id": user_id}
            for t in self.db.old_tweets_2017.find(query_string):
                tweet = Tweet(t)
                self.add_tweet(tweet.author_id, tweet.text, tweet.create_time, self.historical_tweets)
            if count % 1000 == 0:
                logging.info("Historical tweets: {} users done, {} users remain.".format(count, tweet_users))
            count += 1

    def save(self, tvshow_filename='tvshow_tweet.json', histrical_tweets_filename="historical_tweet.json"):
        json.dump(self.tvshow_tweets, open(tvshow_filename, 'w'))
        json.dump(self.historical_tweets, open(histrical_tweets_filename, 'w'))
