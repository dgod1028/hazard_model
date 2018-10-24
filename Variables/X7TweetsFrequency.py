from Variables.Variable import Variable
from Utils.Interactions import Interaction
import math
from Utils.Utils import *
import json
import pickle
from Utils.Filepath import HIS_FREQS

#USER_TOPICS = '../data/lda/his_user_topic.p'   # <- User Topics Files from LDA Model

class X7TweetsFrequency(Variable):
    def __init__(self, g, his_freq_file):
        super().__init__("tweets frequency")
        self.network = g
        self.his_freq = pickle.load(open(his_freq_file, "rb"))

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
        if self.his_freq.get(node):
            total_his_freq = self.his_freq[node]
            return math.log(total_his_freq)
        else:
            return 0
