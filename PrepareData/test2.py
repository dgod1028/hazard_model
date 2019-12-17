import numpy as np
from Utils.Utils import get_mongo_connection, read_users, chunkIt
from Utils.Filepath import USERS, HISTORICAL_COLLECTION, HIS_FREQS, TWEETS_COLLECTION
import time
import pandas as pd
from collections import defaultdict
from datetime import datetime
import pickle as pk

#COLL1 = "ThisIsUs_o"
#COLL2 = "ThisisUs_new"

COLL1 = "TheGoodPlace_o"
COLL2 = "TheGoodPlace_new"

if __name__ =="__main__":

    db = get_mongo_connection()
    #db.his = db[HISTORICAL_COLLECTION]
    #db.new = db[COLL1]
    #print(db.new.find_one())


    nodes = defaultdict(int)
    test = []
    colls = [db[COLL1],db[COLL2]]
    l = colls[0].count() +colls[1].count()
    print("Total : %i" %l)
    count = 0
    for coll in colls:
        for user in coll.find():
            count += 1
            if count % 100000 == 0:
                print("Processing : %i / %i" %(count, l))
            #nodes.append([user["user_id"],user["created_at"]])
            #if user["created_at"] < datetime(2016,1,1):
                #print(user["text"])
            if len(user["entities"]["hashtags"]) > 0:
                for hash in user["entities"]["hashtags"]:
                    if hash["text"]  == "ThisIsUs":
                        if nodes.get(user["user_id"]) is None:
                            nodes[user["user_id"]] = user["created_at"]
                        else:
                            if nodes[user["user_id"]] > user["created_at"]:
                                nodes[user["user_id"]] = user["created_at"]

    pk.dump(nodes,open("data/nodes_GoodPlace.p","wb"))
    print("Finished!")


