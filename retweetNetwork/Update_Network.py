import networkx as nx
from Utils.NetworkUtils import get_graphml
import os

MAIN = '../data/ThisISUS.graphml'
INTER = "../data/TheGoodPlace_interactions_pairs.graphml"


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
if __name__ == "__main__":
    main()