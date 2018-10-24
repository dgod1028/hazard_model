import networkx as nx
from Utils.NetworkUtils import get_graphml
import os
from Utils.Utils import topical_similarity
import pickle
import itertools

MAIN = '../data/ThisISUS.graphml'
INTER = "../data/TheGoodPlace_interactions_pairs.graphml"
USER_TOPIC_FILE = "../data/lda/his_user_topic.p"
USER = '../data/users.p'

def update_jaccard():
    pass
def main():
    inter = get_graphml(INTER)
    main = get_graphml(MAIN)
    dmain = dict(main.nodes)
    for node in inter.nodes:
        #print(dmain[node])
        if dmain.get(node) is not None:
            print("skip")
            inter.node[node]['create_time'] = dmain[node]['create_time']
    print(dict(inter.nodes()))

## If want to add topical_similarity to Network

def add_edge_topical_similarity():
    main = get_graphml(MAIN)
    user_topics = pickle.load(open(USER_TOPIC_FILE,"rb"))
    user_ids = pickle.load(open(USER),'rb')
    """  ## Add all?
    for user1, user2 in itertools.combinations(user_ids):


    """
if __name__ == "__main__":
    add_edge_topical_similarity()