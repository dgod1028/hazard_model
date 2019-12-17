from Variables.Variable import Variable
from Utils.Interactions import Interaction
import math
from Utils.Utils import *
import json
import pickle
import logging

USER_TOPICS = 'data/lda/user_topic_prob.p'   # <- User Topics Files from LDA Model
SPARSE_USER = "data/sparse_user2.p"           # <- User whose tweets frequency is lower than 10 in total.

class X3Topical_Similarity(Variable):
    def __init__(self, g, users, topical_file):
        super().__init__("topical_similarity")
        self.network = g
        self.user_topics = pickle.load(open(USER_TOPICS, "rb"))
        self.sparse_user = pickle.load(open(SPARSE_USER, "rb"))
        self.users = users
        logging.basicConfig(filename="Logging/X3_Topic Miss.log", level=logging.NOTSET, format='%(asctime)s %(message)s')


    def get_covariate(self, node, current_date, nonadopted, step):
        """
        Overwrite get_covariate function
        :param node:
        :param current_date:
        :param nonadopted:
        :return:                sentiment varialbe of node at current_date
        """

        friends = self.network.friends(node, current_date)  ## Get friends list at current time
        friends = [i for i in friends if int(i) in self.users]
        #users = self.network.nodes
        total_topical = 0
        adopted_count = 0

        for user in friends:

            if user not in nonadopted:
                friends_of_friend = self.network.friends(user, current_date)
                ## One way relasion ship [node] -> [user] and [node] <- X [user]
                if node in friends_of_friend:
                    try:
                        total_topical += topical_similarity(self.user_topics[int(user)],self.user_topics[int(node)])
                        adopted_count += 1
                    except:
                        #print("No node %i" % int(user))
                        logging.info("No node %i" % int(user))
                        total_topical += 0
                        adopted_count += 1
        #print("X3 Finished")
        if total_topical <= 0:
            return total_topical
        return math.log(total_topical)