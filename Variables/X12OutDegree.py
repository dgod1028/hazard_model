from Variables.Variable import Variable
from Utils.Interactions import Interaction
import math
from Utils.Utils import *
import json
import pickle
from Utils.Filepath import HIS_FREQS
import pandas as pd


class X12OutDegree(Variable):
    def __init__(self,inout):
        super().__init__("out-degree")
        self.in_out = pd.read_csv(inout,index_col=0)

    def get_covariate(self, node, current_date, nonadopted, step):
        """
        Overwrite get_covariate function
        :param node:
        :param current_date:
        :param nonadopted:
        :return:                1 if hub else 0
        """

        node = int(node)

        if node in self.in_out.index:
            if self.in_out.loc[node, "Out"] > 0:
                return math.log(self.in_out.loc[node, "Out"])
            else:
                return 0
        else:
            return 0

