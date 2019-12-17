from Utils.NetworkUtils import get_graphml
import numpy as np
import pickle as pk

users = []
#nodes = pk.load(open("../data/nodes.p","rb"))
network = get_graphml("../ThisIsUs.graphml")
a = list(map(int,network.nodes))
print(a)
print(len(a))
print(len(set(a)))
#pk.dump(a,open("../data/users.p","wb"))
print(network.edges)