from statsmodels.base.model import GenericLikelihoodModel
import numpy as np
from scipy import stats
import statsmodels.api as sm

class HazardMLE(GenericLikelihoodModel):
#class HazardMLE(sm.OLS):
    def __init__(self, endog, exog, dist=stats.norm):
        super().__init__(endog=endog, exog=exog)
        self.dist = dist
        if self.dist != stats.norm:
            print("Use other distrubtion")

    def loglike(self, params):

        log_likelihood = 0
        # Exog
        #    CONSTANT  ADOPTED_NEIGHBORS  SENTIMENT
        # 0         1                  0  -0.322933
        # 1         1                  0  -0.673151
        # 2         1                 10  -0.749379
        # 3         1                  0  -0.031573
        # 4         1                  2   0.841563

        # Endog
        # Name: ADOPTION
        # 0    0
        # 1    0
        # 2    0
        # 3    0
        # 4    1
        # params = np.asarray([0.3, 0.3, 0.3])
        for exog, endog in zip(self.exog, self.endog):
            if endog == 1:
                log_likelihood += self.dist.logcdf(np.dot(exog, params)).sum()
            elif endog == 0:
                log_likelihood += self.dist.logcdf(-1 * np.dot(exog, params)).sum()
            else:
                assert False, "Shouldn't run into this line"

        # print("{}, {}".format(params, log_likelihood))
        return log_likelihood


def get_hazard_mle_result(exog, endog):
    print(exog.head())
    exit()
    # HazardModel(exog=exog, endog=endog).fit()
