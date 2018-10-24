from pandas import DataFrame
from Utils.NetworkUtils import *
from DynamicNetwork import DynamicNetwork
from scipy import stats
import numpy as np
from HazardMLE import HazardMLE
import logging

class HazardModel:
    def __init__(self, g, variables):
        assert isinstance(g, DynamicNetwork), "Network must be instance of DynamicNetwork"
        self.network = g
        self.variables = variables

    def hazard_mle_estimation(self):
        """
        Input: Dynamic Network, Variables, Adoption Time,
        Output: AdoptedNodesPerStep, Parameters
        """
        # Generate input data for MLE
        ref_result, inputdata = self.generate_MLE_input_data()
        # Remove the first two column "nodeid" and "step", use the last column as endog, use the remain column as exog
        exog, endog = inputdata.iloc[:, 2:-1] ,inputdata.iloc[:, -1]
        print(exog)
        exog.to_csv('data/x.csv',index=False)
        endog.to_csv('data/y.csv',index=False)
        hazard_mle = HazardMLE(exog=exog, endog=endog)
        logging.info("MLE start fiting")

        result = hazard_mle.fit()
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
        intervals = self.network.intervals
        adopted = []

        while non_adopted:
            if stop_step != -1 and step > stop_step:
                break
            non_adopted_temp = []
            num_adopted = 0
            prob_dist[step] = []
            for n in non_adopted:
                covariates = self.get_covariates(n, current_date, frozenset(non_adopted))
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
        for v in self.variables:
            covariates.append(v.get_covariate(node, current_date, nonadopters))
        return covariates

    def generate_MLE_input_data(self, verbose=False):
        non_adopted = self.network.users()  # all node are non-adopted at the begining
        current_date = self.network.start_date
        adopted = []
        mle_input_data = []
        step = 0

        stop_step = self.network.stop_step
        intervals = self.network.intervals

        while non_adopted:
            non_adopted_temp = []
            num_adopted = 0
            for n in non_adopted:
                # Row format [nodeid, step, variable0, ... variablen, adoption]
                row = [n, step]
                for v in self.variables:
                    row.append(v.get_covariate(n, current_date, frozenset(non_adopted)))

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
