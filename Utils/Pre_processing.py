"""
Take all interactions and calculate pair wise jaccard index
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Utils.Interactions import Interaction
import itertools
import pickle
import json
import logging
import signal
import traceback
#import resource
import networkx as nx
import json
import time
from multiprocessing import Pool
from pymongo import MongoClient
from Utils.Utils import *

os.chdir('C:/users/Administrator/Documents/TwitterProject')

INTERACTION_DATA = "data/TheGoodPlace_interactions.p"
USER_FILE = "data/TheGoodPlace.csv"

def main(multi=False,debug=False):
    start = time.time()
    #signal.signal(signal.SIGUSR1, lambda sig, stack: traceback.print_stack(stack))
    inter = Interaction(INTERACTION_DATA, type='p')
    users = list(read_users(USER_FILE))[0:500]
    G = nx.DiGraph()
    G.add_nodes_from(users)
    output = INTERACTION_DATA.rpartition('.')[0]
    logging.basicConfig(filename="preprocess1.log", level=logging.NOTSET, format='%(asctime)s %(message)s')
    if debug:
        print('Cost %.3f s.' % (time.time() - start))
    count = 0
    logging.info("Start")
    if multi:
        p = Pool()

    else:
        for user1, user2 in itertools.combinations(users, 2):
            G.add_edge(user1, user2)
            G[user1][user2]['jac'] = get_stats(user1, user2, inter)
            count += 1
            if count % 10000000 == 0:
                logging.info('{} pairs done'.format(count))
                #logging.info(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
                #print(pair_wise)
                #break
    logging.info("Finished")
    #print(output+"_pairs.graphml")
    nx.write_graphml(G, output+"_pairs.graphml")
    # pickle.dump(pair_wise, open('matrix.p', 'w'))
    # pickle.dump(keymap, open('uid_index_map.p', 'w'))
    # json.dump(pair_wise, open(output + '_pairs.json', 'w'))
    if debug:
        print('Cost %.3f s.' % (time.time() - start))
def get_stats(user1, user2, interactions):
    return interactions.retweet_jaccard(user1, user2)



if __name__ == "__main__":
    main(debug=True,multi=False)