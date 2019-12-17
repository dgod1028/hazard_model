import argparse
import datetime
import logging
import time
import os
import sys

from DynamicNetwork import DynamicNetwork
from HazardModel import HazardModel
from Variables.X0Intercept import *
from Variables.X1RetweetJaccard import *
from Variables.X2Reciprocal import *
from Variables.X3TopicalSimilarity import *
from Variables.XSentiment import *
from Variables.X7TweetsFrequency import *
from Variables.X8TopicalInterest import *
from Variables.X9Official import *
from Variables.X10Hubs import *
from Variables.XTime import *
from Variables.XTimeTrend import *
from Variables.X11InDegree import *
from Variables.X12OutDegree import *

from Utils.NetworkUtils import *
from Utils.Plot import *
from Utils.Filepath import *



WEEK_IN_SECOND = 24 * 60 * 60
STOP_STEP = 13
# See https://github.com/yeqingyan/Sentiment_MaxEnt for program to preprocessing the sentiment data using MaxEnt
#SENTIMENT_DATA = "data/thegoodplace_sentiment_seconds.json"


class DateAction(argparse.Action):
    """
    Convert input string into date in seconds
    """
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(DateAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string):
        start_date = int(time.mktime(datetime.datetime.strptime(values, "%m/%d/%Y").timetuple()))
        setattr(namespace, self.dest, start_date)

def config():
    program_description = "Hazard model"
    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('g', help='Input network graph')
    parser.add_argument('-d', action=DateAction, help='Start date(m/d/y)')
    parser.add_argument('-m', type=int, help="Model Selection (1-8)")
    parser.add_argument('--t', action="store_true", help="If use Time Dummies")
    parser.add_argument('--c', action="store_false", help="If use Constant term")
    parser.add_argument('--trend', action="store_true", help="If use Trend term")

    return vars(parser.parse_args())

def main():
    arguments = config()
    print(arguments)

    t = arguments['t']
    c = arguments['c']
    MODEL = arguments['m']
    trend = arguments['trend']
    FN = MODEL
    if t:
        FN += 100
    if trend:
        FN += 200
    if c is False:
        FN += 1000

    logging.basicConfig(filename="hazardTIU_%i.log" % FN, level=logging.NOTSET, format='%(asctime)s %(message)s')
    with open("hazardTIU_%i.log" %FN,"w"):
        pass
    if os.path.isfile(DYNAMIC_NETWORK):
        g = pickle.load(open(DYNAMIC_NETWORK,"rb"))
    else:
        g = get_graphml(arguments['g'])
        # g = sample(g, 30 / len(g))
        g = DynamicNetwork(g, start_date=arguments['d'], intervals=WEEK_IN_SECOND, stop_step=STOP_STEP)
        pickle.dump(g,open(DYNAMIC_NETWORK,"wb"))
    inter = Interaction(INTERACTION_FILE, "p")

    ## USERS
    #users = pickle.load(open("data/TheGoodPlace_users.p", "rb"))
    users = pickle.load(open("data/users_TIS.p", "rb"))
    #susers = pickle.load(open("data/sparse_user2.p", "rb"))
    #users = [i for i in users if i not in susers]


    # TODO For Swati, put your varialbe here.

    variables = []

    # X0
    if c:
        variables.append(X0Intercept())
    # X1
    if MODEL > 3:
        variables.append(X1RetweetJaccard(users))
    if MODEL > 4:
        variables.append(X2Reciprocal_Neighbors(g,users, inter))
    if MODEL > 5:
        variables.append(X3Topical_Similarity(g, users, USER_TOPICS))
    if MODEL == 7:
        variables.append(XSentiment(g, SENTIMENT_DATA, XSentiment.POSITIVE))      # X4Positive
        variables.append(XSentiment(g, SENTIMENT_DATA, XSentiment.NEUTRAL))  # X4Positive
        variables.append(XSentiment(g, SENTIMENT_DATA, XSentiment.NEGATIVE))  # X4Positive
    if MODEL == 8:
        variables.append(XSentiment(g, SENTIMENT_DATA, XSentiment.POSITIVE))  # X4Positive
    if MODEL == 9:
        variables.append(XSentiment(g, SENTIMENT_DATA, XSentiment.POSITIVE))  # X4Positive
        variables.append(XSentiment(g, SENTIMENT_DATA, XSentiment.NEGATIVE))  # X4Positive
    if MODEL > 2:
        variables += [X7TweetsFrequency(users, HIS_FREQS),
        X8TopicalInterest(USER_TOPICS,[4]),   #
        X9Official(OFFICIAL),
        X10Hubs(HUBS),
        X11InDegree(IN_OUT),X12OutDegree(IN_OUT)]
    if t:
        variables += [XTime(i) for i in range(STOP_STEP - 1)]
    if trend and MODEL > 1:
        variables.append(XTimeTrend())

    """
    variables = [
        X0Intercept(),
        X1RetweetJaccard(users),
        X2Reciprocal_Neighbors(g,users, inter),
        X3Topical_Similarity(g, users, USER_TOPICS),
        #XSentiment(g, SENTIMENT_DATA, XSentiment.POSITIVE),     # X4Positive
        #XSentiment(g, SENTIMENT_DATA, XSentiment.NEUTRAL),      # X5Neutral
        #XSentiment(g, SENTIMENT_DATA, XSentiment.NEGATIVE),     # X6Negative

        X7TweetsFrequency(users, HIS_FREQS),
        X8TopicalInterest(USER_TOPICS,[14]),   ## 1 for movie, 14 for drama
        X9Official(OFFICIAL),
        X10Hubs(HUBS)


    ] #+ [XTime(t) for t in range(STOP_STEP-1)]
    """
    for v in variables:
        assert hasattr(v, 'name'), "Each variable must have a name attribute"
    print(t)

    hazard_model = HazardModel(g, variables,t=t)
    logging.info("Begin MLE estimation")
    # Step 1. MLE estimation
    ref_result, params = hazard_model.hazard_mle_estimation(update=True)

    # Step 2. Hazard model simulation
    sim_result, prob_dist = hazard_model.hazard_simulation(params)
    pickle.dump(sim_result,open("Results/%s_sim_resultTIU.p"%FN,"wb"))
    pickle.dump(prob_dist, open("Results/%s_prob_distTIU.p"%FN, "wb"))
    logging.info(sim_result)
    plot({"Reference": ref_result, "MLE result": sim_result}, show=False,main="plot2_%i.png" % FN)


if __name__ == "__main__":

    main()

