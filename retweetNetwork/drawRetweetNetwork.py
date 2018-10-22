from retweetNetwork.TweetsNetwork import TweetsNetwork
import networkx as nx
from Utils.NetworkUtils import get_graphml
import logging
from retweetNetwork.Tweet import *

TV_SHOW = "ThisIsUs"
FILE = "OLD"  ### <- Change this to Tweets to create Node, "OLD" to create edges.
NODE_GRAPH = '../data/ThisIsUS.graphml'
TWEET_COLL = "tweets"
OLD_COLL = "old_twitter_2017"

if __name__ == "__main__":
    if FILE == "Tweets":   ### 1. Create Graphml File with only Node
        network = TweetsNetwork(TV_SHOW)
        network.add_show(TV_SHOW)
        network.save()
    elif FILE == "OLD":    ### 2. Add edges by using historical data.

        logging.basicConfig(filename= TV_SHOW + ".log", level=logging.INFO, format='%(asctime)s %(message)s')
        logging.info("staring")
        network = TweetsNetwork(TV_SHOW)
        network.network = get_graphml(NODE_GRAPH)
        network.coll = network.db[OLD_COLL]
        count = 0
        for author_id in network.network.nodes():
            query_string = {"user.id": author_id}
            for t in network.coll.find(query_string):
                network.add_tweet(Tweet(t))
            if count % 1000 == 0:
                logging.info("Historical tweets: {} users done, {} users remain.".format(count, network.network.number_of_nodes()))
            if count % 5000 == 0:
                network.save()
            count += 1

        tweet_edges = network.network.number_of_edges()
        logging.info('Analysis historical tweets finished. {} edges added.'.format(tweet_edges))
        network.save()

