from pymongo import MongoClient
import networkx as nx

import logging
from retweetNetwork.Tweet import *
from Utils.Filepath import USERS

class TweetsNetwork:

    # Vertex attribute
    USER_CREATE_TIME    = "create_time"
    #DB_NAME = "old_tweets_2017"
    DB_NAME = 'tweets'

    # Edge attribute
    EDGE_CREATE_TIME    = "create_time"
    EDGE_RETWEET_COUNT  = "retweet_count"
    EDGE_QUOTE_COUNT    = "quote_count"
    EDGE_REPLY_COUNT    = "reply_count"
    EDGE_MENTION_COUNT  = "mention_count"


    def __init__(self, show):
        logging.basicConfig(filename= show + ".log", level=logging.INFO, format='%(asctime)s %(message)s')
        logging.info("staring")
        self.network = nx.DiGraph()
        self.db = MongoClient()['stream_store']
        self.coll = self.db[TweetsNetwork.DB_NAME]
        #print(self.coll.find_one())
        self.show = show

    def add_user(self, user_id, create_time):
        assert isinstance(user_id, int), "User id must be int!"
        if user_id not in self.network:
            self.network.add_node(user_id, create_time = create_time)
            print(self.network.node[user_id])
        else:
            if create_time < self.network.node[user_id][self.USER_CREATE_TIME]:
                self.network.node[user_id][self.USER_CREATE_TIME] = create_time

    def get_tweet_type_count(self, tweet_type):
        if tweet_type is TweetType.RETWEET:
            return self.EDGE_RETWEET_COUNT
        elif tweet_type is TweetType.QUOTE:
            return self.EDGE_QUOTE_COUNT
        elif tweet_type is TweetType.REPLY:
            return self.EDGE_REPLY_COUNT
        elif tweet_type is TweetType.MENTION:
            return self.EDGE_MENTION_COUNT
        else:
            assert False, "Unknown tweet type!"

    def add_edge(self, start, end, tweet_type, create_time):
        assert start in self.network and end in self.network, "User id does not exist!"
        assert isinstance(tweet_type, TweetType), "Tweet type must be instance of TweetType"

        # Add edge
        if self.network.has_edge(start, end):
            if create_time < self.network[start][end][TweetsNetwork.EDGE_CREATE_TIME]:
                self.network[start][end][TweetsNetwork.EDGE_CREATE_TIME] = create_time
        else:
            tmp = TweetsNetwork.EDGE_CREATE_TIME
            self.network.add_edge(start, end,create_time = create_time)

        # Count edge type
        edge_type_count = self.get_tweet_type_count(tweet_type)
        if edge_type_count not in self.network[start][end]:
            self.network[start][end][edge_type_count] = 1
        else:
            self.network[start][end][edge_type_count] += 1

    def add_retweet_edge(self, tweet):
        if tweet.retweet_author_id not in self.network:
            return

        self.add_edge(tweet.author_id, tweet.retweet_author_id, TweetType.RETWEET, tweet.create_time)

    def add_quote_edge(self, tweet):
        if tweet.quote_author_id not in self.network:
            return


        self.add_edge(tweet.author_id, tweet.quote_author_id, TweetType.QUOTE, tweet.create_time)

    def add_mention_edge(self, tweet):
        for mentioned_user in tweet.mentions:
            if (tweet.retweet and mentioned_user in tweet.retweet_mentions) or \
                    (tweet.quote and mentioned_user in tweet.quote_mentions) or \
                    mentioned_user not in self.network:
                continue


            self.add_edge(tweet.author_id, mentioned_user, TweetType.MENTION, tweet.create_time)

    def add_reply_edge(self, tweet):
        if tweet.reply_id not in self.network:
            return


        self.add_edge(tweet.author_id, tweet.reply_id, TweetType.REPLY, tweet.create_time)

    def add_tweet(self, tweet):
        # Retweet do not have any new content, retweet with comment is called quote.
        # Note: It is possible that A retweet a quote, then tweet will contain both retweet_status and quote_status
        # Vice Versa.
        if tweet.retweet:
            self.add_retweet_edge(tweet)

        if tweet.quote:
            self.add_quote_edge(tweet)

        if tweet.mentions:
            self.add_mention_edge(tweet)

        if tweet.reply_id:
            self.add_reply_edge(tweet)

    def add_show(self, show_name):
        """
        Edge: A retweeted B(A follows B)
        A -> B

        Edge: A mentioned B
        A -> B

        If A follows B, A is B's follower, B is A's friend.

        Graph format:
        Node ID: user id in long format
        Node Attribute:
            'active_timestamp':     The first time user post a tweet related to the tv show
        Edge Attribute "Type":
            'R':                    Retweet edge
            'M':                    Mention edge
            'Q':                    Quote edge
            'C':                    Reply edge
            "RMQ":                  Retweet and Mention and Quote edge

        """
        assert show_name != '', "Hashtag shouldn't be empty!"

        # Added tweet author to network
        query_string = {"entities.hashtags.text": show_name}
        logging.info('\nQuery Tweets Begin\nQuery string is ' + str(query_string))
        for t in self.coll.find(query_string):
            #print(t)
            tweet = Tweet(t)
            self.add_user(tweet.author_id, tweet.create_time)
        tweet_users = self.network.number_of_nodes()
        logging.info('Analysis tweets with hashtag {} finished. {} users added.'.format(show_name,tweet_users))

        # Added historical tweets
        count = 0
        for author_id in self.network.nodes():
            query_string = {"user.id": author_id}
            for t in self.coll.find(query_string):
                self.add_tweet(Tweet(t))
            if count % 1000 == 0:
                logging.info("Historical tweets: {} users done, {} users remain.".format(count, tweet_users))
            if count % 5000 == 0:
                self.save()
            count += 1

        tweet_edges = self.network.number_of_edges()
        logging.info('Analysis historical tweets finished. {} edges added.'.format(tweet_edges))

    def save(self, filename='ThisIsUsAdoption_1.graphml'):
        nx.write_graphml(self.network, self.show + ".graphml")
