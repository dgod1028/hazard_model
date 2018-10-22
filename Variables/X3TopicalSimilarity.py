from Variables.Variable import Variable
from Utils.Interactions import Interaction
import math
from Utils.Utils import *
import json

class X1RetweetJaccard(Variable):
    def __init__(self, g, interactions_file,type):
        super().__init__("retweet_jaccard")
        self.network = g
        self.interaction = Interaction(interactions_file,type)

    def get_covariate(self, node, current_date, nonadopted):
        """
        Overwrite get_covariate function
        :param node:
        :param current_date:
        :param nonadopted:
        :return:                sentiment varialbe of node at current_date
        """
        users = self.network.users()
        """
        Fixing
        
        """
