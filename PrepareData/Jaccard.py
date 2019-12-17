from Utils.Utils import *
from Utils.Interactions import Interaction
from tqdm import tqdm
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def collect(u1,user,inter):
    jac = defaultdict()
    for u2 in user:
        try:
            jac[u2] = inter.retweet_jaccard(u1, u2)
        except:
            print("Error with %s and %s" % (u1, u2))
            jac[u2] = inter.retweet_jaccard(u1, u2)
            jac[u2] = 0
    return u1

if __name__ == "__main__":
    import os
    os.chdir("d:/github/hazard_model")
    #user = pickle.load(open("data/ThisIsUs_users.p", "rb"))
    user = pickle.load(open("data/TheGoodPlace_users.p", "rb"))
    suser = pickle.load(open("data/sparse_user2.p", "rb"))
    #nuser = [i for i in user if i not in suser]
    inter = Interaction('data/Interactions.p',"p")
    jaccard = defaultdict()
    N = 0
    C = 0
    excutor = ProcessPoolExecutor()
    """
    for u1 in tqdm(user):

        jaccard[u1] = defaultdict()
        for u2 in user:
            try:
                jaccard[u1][u2] = inter.retweet_jaccard(u1,u2)
            except:
                print("Error with %s and %s" %(u1,u2))
                jaccard[u1][u2] = inter.retweet_jaccard(u1, u2)
                jaccard[u1][u2] = 0

    """
    futures = []
    for u1 in tqdm(user):
        futures.append(excutor.submit(collect,u1,user,inter ) )
    for i, u1 in tqdm(enumerate(user)):
        jaccard[u1] = futures[i].result()
    pickle.dump(jaccard,open("data/jaccard2.p","wb"))



