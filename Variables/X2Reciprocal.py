from Variables.Variable import Variable
from Utils.Interactions import Interaction
import math
from Utils.Filepath import INTERACTION_FILE, SPARSE_USER
import pickle
import logging

USER_TOPICS = '../data/lda/user_topic_prob.p'   # <- User Topics Files from LDA Model
SPARSE_USER = "data/sparse_user2.p"           # <- User whose tweets frequency is lower than 10 in total.

class X2Reciprocal_Neighbors(Variable):
    def __init__(self, g, users, i):
        super().__init__("reciprocal neighbors")
        self.network = g
        self.sparse_user = pickle.load(open(SPARSE_USER, "rb"))
        self.interaction = i
        self.users = users
        logging.basicConfig(filename="Logging/X2_Miss.log", level=logging.NOTSET,
                            format='%(asctime)s %(message)s')

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

        total_reciprocal = 0
        current_influence = []
        total_friends = len(friends)
        #reci_friends = 0
        reci_adopted = 0

        for each_friend in friends:
            friends_of_friend = self.network.friends(each_friend, current_date)

            # find reciprocal friend
            if node in friends_of_friend:
                #reci_friends += 1
                inter_count = self.interaction.interaction_count(node, each_friend)
                total_reciprocal += inter_count
                if self.network.user_adopted_time(each_friend) <= current_date:
                    reci_adopted += 1
                    current_influence.append(inter_count)
        total_influence = 0
        if total_reciprocal == 0:
            return 0
        for influence in current_influence:
            total_influence += float(influence) / float(total_reciprocal)
         #print("{} friends {} reciprocal {} adopted {} influence".format(total_friends, reci_friends, reci_adopted, total_influence))
        if total_influence > 0:
            return math.log(total_influence)
        else:
            return total_influence
