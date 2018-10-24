from Variables.Variable import Variable
from Utils.Interactions import Interaction
import math
from Utils.Utils import *
import json
import pickle
from Utils.Filepath import HIS_FREQS


class X8TopicalInterest(Variable):
    def __init__(self, g, user_topic,ent_topics = None):
        ## ent_topics : one or more topic list which are related to entertainment
        ## Example, if ent_topics = [0,1] , and the user_topic = [0.2, 0.5, 0.1, 0.2] , then
        #           return 0.7 <- (0.2 + 0.5)
        # values in ent_topics must all lower than topic number from LDA
        assert ent_topics is not None, "Please enter topic number list of entertainment. Example: [0,5] or [1]"
        assert isinstance(ent_topics,list), "Type of ent_topics must be list!"
        super().__init__("topical_interest")
        self.network = g
        self.user_topics = pickle.load(open(user_topic, "rb"))
        self.ent_topics = ent_topics


    def get_covariate(self, node, current_date, nonadopted):
        """
        Overwrite get_covariate function
        :param node:
        :param current_date:
        :param nonadopted:
        :return:                sentiment varialbe of node at current_date
        """
        #print(self.his_freq)
        #print(node)
        user_topic = self.user_topics[node]
        self.l = len(user_topic)
        assert all(i < self.l  for i in self.ent_topics ), "All values in ent_topics must smaller than topic number!"
        interest = 0
        check = 0                           ## check if current topic is in ent_topics
        for t in user_topic:
            if check in self.ent_topics:
                interest += t
            check += 1
        if interest <= 0:
            return interest
        else:
            return interest
