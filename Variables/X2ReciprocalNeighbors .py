from Variables.Variable import Variable
from Utils.Interactions import Interaction
import math
from Utils.Filepath import INTERACTION_FILE, SPARSE_USER
import pickle


USER_TOPICS = '../data/lda/user_topic_prob.p'   # <- User Topics Files from LDA Model
SPARSE_USER = "data/sparse_user2.p"           # <- User whose tweets frequency is lower than 10 in total.

class X2Reciprocal_Neighbors(Variable):
    def __init__(self, g):
        super().__init__("reciprocal neighbors")
        self.network = g
        self.sparse_user = pickle.load(open(SPARSE_USER, "rb"))
        self.interaction = Interaction(INTERACTION_FILE, "p")

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
        total = 0
        adopted_count = 0
        user = pickle.load(open("data/TheGoodPlace_users.p", "rb"))
        suser = pickle.load(open("data/sparse_user2.p", "rb"))
        nuser = [i for i in user if i not in suser]

        for user in friends:
            if user != node and user not in nonadopted and int(user) in nuser:
                ## One way relasion ship [node] -> [user] and [node] <- X [user]
                if self.network.network[user].get(node) is not None and self.network.network[node].get(user) is not None:  ## Two-way
                    try:
                        total += self.interaction[int(node)]["interactions"][user]
                        adopted_count += 1
                    except:
                        print("No node %i" % int(user))
                        total += 0
                        adopted_count += 1
        print("X2 Finished")
        if total <= 0:
            return total
        return math.log(total)