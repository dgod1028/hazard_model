from Variables.Variable import Variable
from Utils.Interactions import Interaction
import math
from Utils.Utils import *
import json
import pickle
from Utils.Filepath import HIS_FREQS

#USER_TOPICS = '../data/lda/his_user_topic.p'   # <- User Topics Files from LDA Model

class X9Official(Variable):
    def __init__(self, official_file):
        super().__init__("Official media")
        self.officials = pickle.load(open(official_file, "rb"))

    def get_covariate(self, node, current_date, nonadopted, step):
        """
        Overwrite get_covariate function
        :param node:
        :param current_date:
        :param nonadopted:
        :return:                1 if hub else 0
        """

        node = int(node)

        if node in self.officials:
            return 1
        else:
            return 0
