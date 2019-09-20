from Utils.Utils import get_mongo_connection
from Utils.Filepath import HISTORICAL_COLLECTION
from bson.json_util import dumps
import pickle as pk
if __name__ == "__main__":
    d = get_mongo_connection()
    nodes = pk.load(open("data/nodes.p","rb"))
    print(nodes)
    coll = d[HISTORICAL_COLLECTION]
    print(coll.find_one())