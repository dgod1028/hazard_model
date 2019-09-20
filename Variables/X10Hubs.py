from Variables.Variable import Variable
from Utils.Interactions import Interaction
import math
from Utils.Utils import *
import json
import pickle
from Utils.Filepath import HIS_FREQS

#USER_TOPICS = '../data/lda/his_user_topic.p'   # <- User Topics Files from LDA Model

class X10Hubs(Variable):
    def __init__(self, hubs_file):
        super().__init__("influential hubs")
        self.hubs = pickle.load(open(hubs_file, "rb"))

    def get_covariate(self, node, current_date, nonadopted):
        """
        Overwrite get_covariate function
        :param node:
        :param current_date:
        :param nonadopted:
        :return:                1 if hub else 0
        """

        node = int(node)

        if node in self.hubs:
            return 1
        else:
            return 0
