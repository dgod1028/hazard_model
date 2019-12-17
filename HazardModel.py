from pandas import DataFrame
from Utils.NetworkUtils import *
from DynamicNetwork import DynamicNetwork
from scipy import stats
import numpy as np
from HazardMLE import HazardMLE
import logging
import pickle
from Utils.Filepath import SPARSE_USER, INTERACTION_FILE, USERS
from Utils.Interactions import Interaction

from multiprocessing import Pool
from functools import partial
from tqdm import tqdm
import os
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler


def make_row(n, current_date, non_adopted, v):
    return v.get_covariate(n, current_date, frozenset(non_adopted))

class HazardModel:
    def __init__(self, g, variables,t=True,model=0):
        assert isinstance(g, DynamicNetwork), "Network must be instance of DynamicNetwork"
        self.network = g
        self.variables = variables
        self.users = pickle.load(open(USERS, "rb"))
        self.interaction = Interaction(INTERACTION_FILE, "p")
        self.t = t
        self.model = model

    def  hazard_mle_estimation(self,update = True):
        """
        Input: Dynamic Network, Variables, Adoption Time,
        Output: AdoptedNodesPerStep, Parameters
        """
        # Generate input data for MLE

        # Remove the first two column "nodeid" and "step", use the last column as endog, use the remain column as exog
        if update or (os.path.isfile("data/x.csv") is False) or (os.path.isfile("data/ref_result.p") is False) :
            print("No data, start creating...")
            ref_result, inputdata = self.generate_MLE_input_data()
            exog, endog = inputdata.iloc[:, 2:-1] ,inputdata.iloc[:, -1]
            print(exog)
            exog.to_csv('data/x2_%i.csv' %self.model,index=False)
            endog.to_csv('data/y2.csv',index=False)
            #nx = exog
            #if nx.shape[1] > 1:
            #    nx.iloc[:, 1:] = StandardScaler().fit_transform(exog.iloc[:,1:])

            #nx.to_csv('data/x.csv', index=False)
            #exog = nx
            pickle.dump(ref_result,open("data/ref_result.p","wb"))

        else:
            exog = pd.read_csv("data/x.csv").loc[:,[v.name for v in self.variables]]
            endog = pd.read_csv("data/y.csv",header=None)
            ref_result = pickle.load(open("data/ref_result.p","rb"))
        print(", ".join([v.name for v in self.variables]))
        print("Data Prepared...")
        hazard_mle = HazardMLE(exog=exog, endog=endog)
        logging.info("MLE start fitting")
        print("MLE start fitting")

        result = hazard_mle.fit(maxiter=10000)
        # Note `summary()` might not work on small samples, since it didn't know how to normalized a vector of zeros
        logging.info(result.summary())
        logging.info("MLE loglikelihood")
        self.print_loglikelihood(exog, endog, result.params)
        return ref_result, result.params

    def hazard_simulation(self, parameters, verbose=False):
        """
        Input: Dynamic Network, Variables, Parameters
        Output: Hazard Rate
        """

        prob_dist = {}
        step = 0
        current_date = self.network.start_date
        stop_step = self.network.stop_step
        non_adopted = self.network.users()
        non_adopted = [i for i in non_adopted if int(i) in self.users]  ######
        intervals = self.network.intervals
        adopted = []
        while non_adopted:
            print("Now Processing %i / %i" %(step, stop_step))
            if stop_step != -1 and step >= stop_step:
                break
            non_adopted_temp = []
            num_adopted = 0
            prob_dist[step] = []
            for n in non_adopted:
                self.step = step
                #covariates = self.get_covariates(n, current_date, frozenset(non_adopted))
                covariates = []
                if self.t:
                    for v in self.variables[:-(stop_step - 1)]:
                        covariates.append(v.get_covariate(n, current_date, frozenset(non_adopted),step))
                    ## Time
                    tmp = [0] * (stop_step)
                    tmp[step] = 1
                    covariates += tmp[:-1]
                else:
                    for v in self.variables:
                        covariates.append(v.get_covariate(n, current_date, frozenset(non_adopted),step))


                adopted_probability = stats.norm.cdf(np.dot(covariates, parameters))

                prob_dist[step].append(adopted_probability)
                u = random.uniform(0, 1)

                if adopted_probability >= 0 and u <= adopted_probability:
                    num_adopted += 1
                else:
                    non_adopted_temp.append(n)

            non_adopted = non_adopted_temp
            if adopted == []:
                adopted.append(num_adopted)
            else:
                adopted.append(num_adopted + adopted[-1])
            current_date += intervals
            step += 1
        return adopted, prob_dist

    def get_covariates(self, node, current_date, nonadopters):
        covariates = []
        for v in self.variables[:-(self.network.stop_step)]:
            covariates.append(v.get_covariate(node, current_date, nonadopters))
        return covariates

    def generate_MLE_input_data(self, verbose=False):
        non_adopted = self.network.users()  # all node are non-adopted at the begining

        non_adopted = [i for i in non_adopted if int(i) in self.users]          ###### Exclued those without Interactions
        current_date = self.network.start_date
        adopted = []
        mle_input_data = []
        step = 0

        stop_step = self.network.stop_step
        intervals = self.network.intervals
        #print(stop_step)

        while non_adopted:
            print("Now Processing %i / %i" % (step, stop_step))
            non_adopted_temp = []
            num_adopted = 0
            self.step = step
            for n in tqdm(non_adopted):
                # Row format [nodeid, step, variable0, ... variablen, adoption]
                row = [n, step]

                if self.t:
                    for v in self.variables[:-(stop_step-1)]:
                        row.append(v.get_covariate(n, current_date, frozenset(non_adopted),step))
                    ## Time
                    tmp = [0] * stop_step
                    tmp[step] = 1
                    row += tmp[:-1]
                else:
                    for v in self.variables:
                        row.append(v.get_covariate(n, current_date, frozenset(non_adopted),step))


                adoption = 0
                if self.network.user_adopted_time(n) <= current_date:
                    adoption = 1
                    num_adopted += 1
                else:
                    non_adopted_temp.append(n)
                row.append(adoption)
                mle_input_data.append(row)
            non_adopted = non_adopted_temp
            if adopted == []:
                adopted.append(num_adopted)
            else:
                adopted.append(num_adopted + adopted[-1])
            current_date += intervals
            step += 1
            #print(mle_input_data)
            #print(len(mle_input_data))
            #print(len(mle_input_data[0]))
            if stop_step != -1 and step >= stop_step:
                break
        return adopted, DataFrame(mle_input_data, columns=["ID", "Step"] + [v.name for v in self.variables] + ["Adoption"])

    def print_loglikelihood(self, exogs, endogs, params, dist=stats.norm):
        exogs = np.asarray(exogs)
        endogs = np.asarray(endogs)
        log_likelihood = 0

        for exog, endog in zip(exogs, endogs):
            if endog == 1:
                log_likelihood += dist.logcdf(np.dot(exog, params)).sum()
            elif endog == 0:
                log_likelihood += dist.logcdf(-1 * np.dot(exog, params)).sum()
            else:
                assert False, "Shouldn't run into this line"

        logging.info("{}, {}".format([round(i, 5) for i in params], log_likelihood))
