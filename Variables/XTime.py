import json
from Variables.Variable import Variable
from Utils.Utils import *

"""
    XTime for X11(t)
"""

class XTime(Variable):

    def __init__(self, time):

        super().__init__("Time %i" % time)
        self.time = time

    def get_covariate(self, node, current_date, nonadopted):
        """
        Return number of specific sentiment a node received from its adopted neighbor.
        At step 0, the value should be 0, since no neighbor is adopted.

        :param node: 
        :param current_date: 
        :param nonadopted: 
        :return:                sentiment varialbe of node at current_date 
        """

        if current_date == self.time:
            return 1
        else:
            return 0

