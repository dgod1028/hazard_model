import pandas as pd
import numpy as np
import pickle
from tqdm import tqdm

"""
inter2 = pickle.load(open("d:/github/hazard_model/data/interactions.p", "rb"))
in_out = pd.DataFrame(np.zeros((len(inter2.keys()), 2)))
in_out.index = inter2.keys()
in_out.columns = ["In", "Out"]
users = inter2.keys()
for u1, v in tqdm(inter2.items()):
    in_out.loc[u1, "Out"] = sum(v["interactions"].values())
    for u2, i in v["interactions"].items():
        if int(u2) in users:
            in_out.loc[int(u2), "In"] += i

in_out.to_csv("../data/in_out.csv")
"""

in_out = pd.read_csv("../data/in_out.csv",index_col=0)

sd = in_out.std()
threshold_1 = 3 * sd["In"]
threshold_2 = 3 * sd["Out"]
hubs = []
for u in in_out.index:
    if in_out.loc[u,"In"] > threshold_1 and in_out.loc[u,"Out"] > threshold_2:
        hubs.append(u)

pickle.dump(hubs,open("../data/hubs.p","wb"))
