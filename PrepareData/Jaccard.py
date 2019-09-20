from Utils.Utils import *
from Utils.Interactions import Interaction
from tqdm import tqdm
from collections import defaultdict

if __name__ == "__main__":
    import os
    os.chdir("d:/github/hazard_model")
    user = pickle.load(open("data/TheGoodPlace_users.p", "rb"))
    suser = pickle.load(open("data/sparse_user2.p", "rb"))
    nuser = [i for i in user if i not in suser]
    inter = Interaction('data/Interactions.p',"p")
    jaccard = defaultdict()

    for u1 in tqdm(nuser):
        jaccard[u1] = defaultdict()
        for u2 in nuser:
            try:
                jaccard[u1][u2] = inter.retweet_jaccard(u1,u2)
            except:
                print("Error with %i and %i" %(u1, u2))
                jaccard[u1][u2] = 0

    pickle.dump(jaccard,open("data/jaccard.p","wb"))



