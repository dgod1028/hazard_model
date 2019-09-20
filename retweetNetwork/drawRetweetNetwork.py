from retweetNetwork.TweetsNetwork import TweetsNetwork
import networkx as nx
from Utils.NetworkUtils import get_graphml
import logging
from retweetNetwork.Tweet import *
from Utils.Filepath import TWEETS_COLLECTION, HISTORICAL_COLLECTION
from multiprocessing import Pool

TV_SHOW = ["ThisIsUs","TheGoodPlace","24Legacy"]
FILE = "OLD"  ### <- Change this to Tweets to create Node, "OLD" to create edges.
NODE_GRAPH = 'data/nodes.graphml'
TWEET_COLL = TWEETS_COLLECTION
OLD_COLL = HISTORICAL_COLLECTION
#ALL = {"ThisIsUs":{"tweets":["ThisIsUs_o","ThisIsUs_n"]}

def add_node(show):
    print("Start %s" % show)
    network = TweetsNetwork(show)
    # network.network = get_graphml(NODE_GRAPH)  ## Load graphml file build by tweets
    network.add_show(show)
    network.save()
    print("%s Finished" %show)

def add_edge(show):
    logging.basicConfig(filename=show + ".log", level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info("staring")
    network = TweetsNetwork(show)  ##
    network.network = get_graphml(show+".graphml")  ## Load graphml file build by tweets
    network.colls = []
    for coll in OLD_COLL:
        network.colls.append(network.db[coll])
    #network.coll = network.db[OLD_COLL]  ## Read collections[old_tweets_2017]
    count = 0
    # print(network.network.nodes)
    l = 0
    for coll in network.colls:
        l += coll.count()
    ids = network.network.nodes()
    # print("###")
    # print("53540257" in network.network)
    for coll in network.colls:
        for t in coll.find():
            try:
                if str(t["user_id"]) in ids:
                    network.add_tweet(Tweet(t))
            except:
                try:
                    if str(t["user"]["id"]) in ids:
                        network.add_tweet(Tweet(t))
                except:
                    print("# Error! ")
                    print(t)
                    pass
            if count % 100000 == 0:
                logging.info(
                    "Historical tweets: {} users done, {} users remain.".format(count, network.network.number_of_nodes()))
            if count % 1000000 == 0:
                network.save()
                print("Process : %i / %i" % (count, l))
            count += 1

    tweet_edges = network.network.number_of_edges()
    logging.info('Analysis historical tweets finished. {} edges added.'.format(tweet_edges))
    network.save()

if __name__ == "__main__":
    if FILE == "Tweets":   ### 1. Create Graphml File with Node and edges by using Tweets Data
        p = Pool()
        p.map(add_node,TV_SHOW)
        p.close()

    elif FILE == "OLD":    ### 2. Add edges by using Historical data.
        p = Pool()
        p.map(add_edge,TV_SHOW)
        p.close()


