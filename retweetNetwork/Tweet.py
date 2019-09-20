import datetime
from enum import Enum

class TweetType(Enum):
    RETWEET = 1
    QUOTE = 2
    REPLY = 3
    MENTION = 4

class Tweet:
    MENTION = "user_mentions"
    QUOTE_FIELD = "quoted_status"
    REPLY_FIELD = "in_reply_to_user_id"
    RETWEET_FIELD = "retweeted_status"

    def __init__(self, tweet):
        self.tweet = tweet
        try:
            self.author_id = str(self.tweet['user_id'])
            self.create_time = int(
                datetime.datetime.strptime(str(self.tweet['created_at']), "%Y-%m-%d %H:%M:%S").timestamp())
        except:
            self.author_id = str(self.tweet['user']['id'])
            self.create_time = int(
                datetime.datetime.strptime(str(self.tweet['created_at']), "%a %b %d %H:%M:%S +0000 %Y").timestamp())

        #%a %b %d %H:%M:%S %z %Y

        # Retweet field
        if Tweet.RETWEET_FIELD in tweet:
            self.retweet = True
            self.retweet_author_id = str(tweet[Tweet.RETWEET_FIELD]["user"]["id"])
            self.retweet_mentions = [int(user['id']) for user in tweet[Tweet.RETWEET_FIELD]["entities"][Tweet.MENTION]]
        else:
            self.retweet = False
            self.retweet_author_id = None
            self.retweet_mentions = None

        # Quote field
        if Tweet.QUOTE_FIELD in tweet:
            self.quote = True
            self.quote_author_id = str(tweet[Tweet.QUOTE_FIELD]["user"]["id"])
            self.quote_mentions = [int(user['id']) for user in tweet[Tweet.QUOTE_FIELD]["entities"][Tweet.MENTION]]
        else:
            self.quote = False
            self.quote_author_id = None

        # Mention field
        if Tweet.MENTION in tweet["entities"]:
            self.mentions = [str(user['id']) for user in tweet["entities"][Tweet.MENTION]]
        else:
            self.mentions = None

        # Reply field
        if Tweet.REPLY_FIELD in tweet and tweet[Tweet.REPLY_FIELD]:
            self.reply_id = str(tweet[Tweet.REPLY_FIELD])
        else:
            self.reply_id = None

