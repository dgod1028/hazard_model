
from tqdm import tqdm
import pickle as pk
from random import seed
import numpy as np
import pandas as pd
from statsmodels.distributions.empirical_distribution import ECDF
import copy
from gensim.models.ldamulticore import LdaMulticore

def ecdf(data):
    # create a sorted series of unique data
    cdfx = np.sort(data)
    ind = np.argsort(data)
    # x-data for the ECDF: evenly spaced sequence of the uniques
    x_values = np.linspace(start=min(cdfx),
                           stop=max(cdfx), num=len(cdfx))

    size_data = data.size
    y_values = []
    # y-data for the ECDF:-104values = []
    for i in x_values:
        # all the values in raw data less than the ith value in x_values
        temp = data[data <= i]
        # fraction of that value with respect to the size of the x_values
        value = temp.size / size_data
        # pushing the value in the y_values
        y_values.append(value)
    # return both x and y values
    return x_values, y_values,ind
def frex(phi,mu,w):
    return 1/(w/phi+(1-w)/mu)

def topwords(beta,mode = "freq",list=None):
    #sorted_phi = np.zeros()
    toplist = []
    topprob = []
    print(beta)
    phi = (beta + model.beta) / (beta.sum(axis=0, keepdims=True) + (model.beta * model._V))
    print(pd.DataFrame(phi))
    if mode == "freq":
        toplist = np.argsort(phi)[:,::-1].tolist() # Reverse
        topprob = np.sort(phi)[:,::-1]
        topprob = topprob.tolist()
    elif mode == "frex":
        nkv = copy.deepcopy(model.nkv)
        print("Mode:Frex")
        for i in tqdm(range(phi.shape[0])):
            ephi = ECDF(phi[i,:])
            phi[i, :] = ephi(phi[i, :])
        nnkv = copy.deepcopy(model.nkv)
        for i in tqdm(range(model.nkv.shape[1])):
            enkv = ECDF(nnkv[:,i])
            nkv[:,i] = enkv(nnkv[:,i])
        fe = frex(phi,nkv,1)
        print(fe)
        toplist = np.argsort(fe)[:,::-1].tolist() # Reverse
        topprob = np.sort(fe)[:,::-1]
        topprob = topprob.tolist()

        import matplotlib.pyplot as plt



    return [toplist,topprob]

def top_words_table(topwords, jlist=None, type="category",prob=False):
    """
    :param topwords: [toplist, topprob] from topwords()
    :param jlist    : {1:[*Jan*,*JICFS*,*Jan Name*,*JICFS Name*],2:...}
    :param type    : "category": convert to category, "jan": convert to JAN code
    :return:
    """
    k = len(topwords[0])
    words = topwords[0].copy()
    print("Start make table....")
    if prob:
        pass
    else:
        for wk in tqdm(range(len(words))):
            for w in range(len(words[wk])):
                if jlist is not None:
                    if type == "category":
                        tmp = jlist[topwords[0][wk][w]][3]
                    elif type == "jan":
                        tmp = jlist[topwords[0][wk][w]][2]
                    words[wk][w] = '[%i] %s' % (topwords[0][wk][w], tmp)
                else:
                    words[wk][w] = topwords[0][wk][w]
    words = pd.DataFrame(words).T
    print(words)
    return words




if __name__ == "__main__":
    T = 20
    model = LdaMulticore.load('../data/LDA/his_LDA_%i.lda' % T)
    # id2jan   -> {1,[*
    #id2jan = pk.load(open('id2jan.p','rb'))


    top = topwords(model.nkv,"frex")
    table = top_words_table(top)
    table.iloc[:20,:].to_csv("topwords(1).csv",encoding="utf_8_sig")




