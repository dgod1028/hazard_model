import argparse
import datetime
import logging
import time

from DynamicNetwork import DynamicNetwork
from HazardModel import HazardModel
from Variables.X0Intercept import *
from Variables.X1RetweetJaccard import *
from Variables.XSentiment import *
from Variables.X3TopicalSimilarity import *
from Utils.NetworkUtils import *
from Utils.Plot import *

WEEK_IN_SECOND = 7 * 24 * 60 * 60
STOP_STEP = 13
# See https://github.com/yeqingyan/Sentiment_MaxEnt for program to preprocessing the sentiment data using MaxEnt
#SENTIMENT_DATA = "data/thegoodplace_sentiment_seconds.json"
USER_TOPICS = 'data/lda/his_user_topic.p'   # <- User Topics Files from LDA Model


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
    return vars(parser.parse_args())

def main():
    arguments = config()
    print(arguments)
    g = get_graphml(arguments['g'])
    print(type(g))
    # g = sample(g, 30 / len(g))

    g = DynamicNetwork(g, start_date=arguments['d'], intervals=WEEK_IN_SECOND, stop_step=STOP_STEP)
    # TODO For Swati, put your varialbe here.
    variables = [
        X0Intercept(),
        X1RetweetJaccard(g,'data/Interactions.p',type="p"),
        #XSentiment(g, SENTIMENT_DATA, XSentiment.POSITIVE),     # X4Positive
        #XSentiment(g, SENTIMENT_DATA, XSentiment.NEUTRAL),      # X5Neutral
        #XSentiment(g, SENTIMENT_DATA, XSentiment.NEGATIVE),     # X6Negative
        X3Topical_Similarity(g,USER_TOPICS)
    ]
    for v in variables:
        assert hasattr(v, 'name'), "Each variable must have a name attribute"

    hazard_model = HazardModel(g, variables)
    logging.info("Begin MLE estimation")
    # Step 1. MLE estimation
    ref_result, params = hazard_model.hazard_mle_estimation()

    # Step 2. Hazard model simulation
    sim_result, prob_dist = hazard_model.hazard_simulation(params)
    logging.info(sim_result)
    plot({"Reference": ref_result, "MLE result": sim_result}, show=False)

if __name__ == "__main__":
    logging.basicConfig(filename="hazard.log", level=logging.NOTSET, format='%(asctime)s %(message)s')
    main()

