"""
creates the interactions input file from the database
where all interactions of the users are stored

"""
from pymongo import MongoClient
import pickle
import json
import logging

# TODO move this to some global setting


USER_FILE = "../data/TheGoodPlace.csv"
INTERACTION_COLLECTION = "Interactions"

def main():
    output_dir = USER_FILE.rpartition('.')[0]
    init_logging(output_dir + '_log.log')
    db = get_mongo_connection()
    coll = db[INTERACTION_COLLECTION]
    users = read_users(USER_FILE)
    users = list(users)[:500]
    interactions = get_interactions(users, coll)
    pickle.dump(interactions, open(output_dir + '_interactions.p', 'wb'))
    json.dump(interactions, open(output_dir + '_interactions.json', 'w'))


def init_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(message)s')


def get_interactions(users, coll):
    interactions = dict()
    done = 0
    no_data = 0
    for user in users:
        inter = coll.find_one({'id' : user}, {'_id': False})
        if not inter:
            no_data += 1
        interactions[user] = inter
        done += 1
        if done % 1000 == 0 :
            logging.info("done {}, no data = {}".format(done, no_data))
    return interactions


def read_users(user_file):
    with open(user_file, 'rb') as f:
        users = map(int, f.readlines())
    return users


def get_mongo_connection(host="127.0.0.1", port=27017, db_name="stream_store"):
    return MongoClient(host=host, port=port)[db_name]


if __name__ == "__main__":
    main()