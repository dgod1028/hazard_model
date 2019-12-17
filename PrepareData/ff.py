import pickle as pkl
"""
u1 = pkl.load(open("../data/lda/perplexity_20.p","rb"))
u2 = pkl.load(open("../data/lda/perplexity_30.p","rb"))
u3 = pkl.load(open("../data/lda/perplexity_40.p","rb"))
print(u1)
print(u2)
print(u3)
"""
his = pkl.load(open("../data/historical_frequencys.p","rb"))
print(his)
print(len(his))
print(sorted(his.values()))

sparse_user = []
for k,v in his.items():
    if v < 11:
        sparse_user.append(k)
print(sparse_user)
pkl.dump(sparse_user,open("../data/sparse_user.p","wb"))