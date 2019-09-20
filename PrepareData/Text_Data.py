from Utils.Utils import get_mongo_connection
from tqdm import tqdm
from collections import defaultdict
import datetime
import json
import pickle
from textblob import TextBlob
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing
import datetime

COLLS = ['TheGoodPlace_new','TheGoodPlace_o','old_tweets','old_tweets_2017']
MEDIA = "../data/news_media_handles.txt"

lines = open(MEDIA, "r").readlines()
media = [i.rstrip() for i in lines]
i = 2
def process_cursor(skip_n,limit_n):
    print('Starting process',skip_n//limit_n,'...')
    tweets = defaultdict()
    collection = get_mongo_connection()[COLLS[i]]
    cursor = collection.find({}).skip(skip_n).limit(limit_n)
    official = []
    task_id = skip_n // limit_n
    for count, t in enumerate(cursor):
        if count % 1000000 == 0:
            now = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print("%s   #Task %i:  %i / %i" %(now, task_id, count, limit_n))
        # for example:
        try:
            user = int(t["user_id"])
            name = t["screen_name"]
        except:
            try:
                user = int(t["user"]["id"])
                name = t["user"]["screen_name"]
            except:
                print(t)
                continue

        if name in media and name not in official:
            official.append(user)
        try:
            create_time = int(t['created_at'].timestamp())
        except:
            try:
                create_time = int(datetime.datetime.strptime(t['created_at'], "%a %b %d %H:%M:%S %z %Y").timestamp())
            except:
                print(t["created_at"])
                print(int(datetime.datetime.strptime(t['created_at'], "%a %b %d %H:%M:%S %z %Y").timestamp()))
                continue
        text = t["text"]
        sent = TextBlob(text).sentiment[0]
        if sent > 0:
            sent = 1
        elif sent < 0:
            sent = -1
        else:
            sent = 0
        if user not in tweets.keys():
            tweets[user] = defaultdict()
        tweets[user][create_time] = sent
    print('Completed process', skip_n // limit_n, '...')
    json.dump(tweets, open("../data/his/Tweets_%i_%i.json" % (i, task_id), "w"))
    pickle.dump(official, open("../data/his/official_%i_%i.p" % (i,task_id), "wb"))
    #return tweets, official



def collect_text(collection):
    tweets = defaultdict()
    coll = db[collection]
    l = coll.count()
    #l = 5000
    official = []
    for t in tqdm(coll.find(),total=l):
        try:
            user = int(t["user_id"])
            name = t["screen_name"]
        except:
            try:
                user = int(t["user"]["id"])
                name = t["user"]["screen_name"]
            except:
                continue

        if name in media and name not in official:
            official.append(user)
        try:
            create_time = int(t['created_at'].timestamp())
        except:
            try:
                create_time = int(datetime.datetime.strptime(t['created_at'], "%a %b %d %H:%M:%S %z %Y").timestamp())
            except:
                continue
        text = t["text"]
        sent = TextBlob(text).sentiment[0]
        if sent > 0:
            sent = 1
        elif sent < 0:
            sent = -1
        else:
            sent = 0
        if user not in tweets.keys():
            tweets[user] = defaultdict()
        tweets[user][create_time] = sent
    #json.dump(tweets, open("../data/his/Tweets_%i_%i.json" % (i,skip_n // limit_n), "w"))
    #pickle.dump(offical, open("../data/his/official_%i.p" % i, "wb"))
    return tweets, official



if __name__ == "__main__":

    n_cores = 10
    db = get_mongo_connection()
    collection_size = db[COLLS[i]].count()
    batch_size = round(collection_size/n_cores+0.5)
    skips = range(0, n_cores*batch_size, batch_size)

    #tweets, offical = collect_text(COLLS[i])
    processes = [ multiprocessing.Process(target=process_cursor, args=(skip_n,batch_size)) for skip_n in skips]

    for process in processes:
        process.start()

    for process in processes:
        process.join()


    #json.dump(tweets,open("../data/Tweets_%i.json" % i,"w"))
    #pickle.dump(offical,open("../data/official_%i.p"% i, "wb"))
