from Variables.Variable import Variable
from Utils.Interactions import Interaction
import math
from Utils.Utils import *
import json
import pickle


USER_TOPICS = '../data/lda/his_user_topic.p'   # <- User Topics Files from LDA Model

class X3Topical_Similarity(Variable):
    def __init__(self, g, topical_file):
        super().__init__("topical_similarity")
        self.network = g
        self.user_topics = pickle.load(open(topical_file, "rb"))

    def get_covariate(self, node, current_date, nonadopted):
        """
        Overwrite get_covariate function
        :param node:
        :param current_date:
        :param nonadopted:
        :return:                sentiment varialbe of node at current_date
        """

        friends = self.network.friends(node, current_date)  ## Get friends list at current time
        #users = self.network.nodes
        total_topical = 0
        adopted_count = 0


        for user in friends:
            if user != node and user not in nonadopted:
                ## One way relasion ship [node] -> [user] and [node] <- X [user]
                if self.network.network[user].get(node) is None:
                    total_topical += topical_similarity(self.user_topics[user],self.user_topics[node])
                    adopted_count += 1
        if total_topical <= 0:
            return total_topical
        return math.log(total_topical)