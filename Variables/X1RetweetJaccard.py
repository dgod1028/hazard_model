from Variables.Variable import Variable
from Utils.Interactions import Interaction
import math
from Utils.Utils import *
from Utils.Filepath import SPARSE_USER, JACCARD, USERS
import json
import logging

class X1RetweetJaccard(Variable):
    def __init__(self, users):
        super().__init__("retweet_jaccard")
        #self.network = g
        #self.interaction = Interaction(interactions_file,type)
        self.jaccard = pickle.load(open(JACCARD,"rb"))
        self.users = users
        logging.basicConfig(filename="Logging/X1_Miss.log", level=logging.NOTSET,
                            format='%(asctime)s %(message)s')

    def get_covariate(self, node, current_date, nonadopted):
        """
        Overwrite get_covariate function
        :param node:
        :param current_date:
        :param nonadopted:
        :return:                sentiment varialbe of node at current_date
        """
        #users = self.users
        total_jaccard = 0
        adopted_count = 0
        for user in self.users:
            try:
                if str(user) not in nonadopted:
                    #total_jaccard += self.interaction.retweet_jaccard(int(node), int(user))
                    total_jaccard += self.jaccard[int(node)][user]
                    adopted_count += 1
            except:
                #logging.info("No User %i" % int(user))
                total_jaccard += 0
                adopted_count += 1
        #print("X1 Finished")
        if total_jaccard <= 0:
            return total_jaccard

        return math.log(total_jaccard)


