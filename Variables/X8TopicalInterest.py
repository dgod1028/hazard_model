from Variables.Variable import Variable
from Utils.Interactions import Interaction
import math
from Utils.Utils import *
import json
import pickle
from Utils.Filepath import HIS_FREQS
import logging

USER_TOPICS = 'data/lda/user_topic_prob.p'    # User Topics Files from LDA Model
class X8TopicalInterest(Variable):
    def __init__(self, user_topic, ent_topics = None):
        ## ent_topics : one or more topic list which are related to entertainment
        ## Example, if ent_topics = [0,1] , and the user_topic = [0.2, 0.5, 0.1, 0.2] , then
        #           return 0.7 <- (0.2 + 0.5)
        # values in ent_topics must all lower than topic number from LDA
        assert ent_topics is not None, "Please enter topic number list of entertainment. Example: [0,5] or [1]"
        assert isinstance(ent_topics,list), "Type of ent_topics must be list!"
        super().__init__("topical_interest")
        self.user_topics = pickle.load(open(USER_TOPICS, "rb"))
        self.ent_topics = ent_topics
        logging.basicConfig(filename="Logging/X8_Miss.log", level=logging.NOTSET,
                            format='%(asctime)s %(message)s')


    def get_covariate(self, node, current_date, nonadopted, step):
        """
        Overwrite get_covariate function
        :param node:
        :param current_date:
        :param nonadopted:
        :return:                sentiment varialbe of node at current_date
        """
        #print(self.his_freq)
        #print(node)
        try:
            user_topic = self.user_topics[int(node)]
            self.l = len(user_topic)
            assert all(i < self.l  for i in self.ent_topics ), "All values in ent_topics must smaller than topic number!"
            interest = 0
            check = 0                           ## check if current topic is in ent_topics
            for k, t in enumerate(user_topic):
                if k in self.ent_topics:
                    interest += t
            #print("X8 Finished")
            return interest
        except:
            #logging.info("Missing for Node %i" % int(node))
            return 0