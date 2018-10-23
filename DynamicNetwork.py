import random
import networkx as nx

class DynamicNetwork:
    # Node attribute 'create_time' and edge attribute 'create_time' are different attributes.
    # Node's 'create_time' is the node's adoption time.
    # Edge's 'create_time' is when that edge created.
    ADOPTION_TIME = 'create_time'
    EDGE_CREATE_TIME = 'create_time'

    def __init__(self, g, start_date=None, intervals = None, stop_step = None):
        assert isinstance(g, nx.DiGraph), "Network must be instance of DiGraph"
        self.network = g
        # if sentiment_data == {}:
        #     self.fake_sentiment = True
        #     self.sentiment_data = {}
        # else:
        """
            Real sentiment data format
            {   "user_id1":
                    {   "timestamp1":   sentimentValue1,
                        "timestamp2":   sentimentValue2
                    }
                "user_id2":
                    {   "timestamp1":   sentimentValue1,
                        "timestamp2":   sentimentValue2
                    }
            }   
        """
        assert isinstance(intervals, int)
        assert start_date != None
        assert stop_step != None
        self.fake_sentiment = False
        self.start_date = start_date
        self.intervals = intervals
        self.stop_step = stop_step

    def users(self):
        return self.network.nodes()

    def user_adopted_time(self, node):
        # A node's create time is its adopted time.
        return self.network.node[node][self.ADOPTION_TIME]

    def friends(self, node, current_date):
        """ Return Twitter user's friends before the current_date
        A --> B means B is successor in our case, it means A retweets B thus B influences A
        This pattern applies to quote reply and mentions

        :param node:                Current node
        :param current_date:        Date
        :return:                    Friends list
        """

        friends = []

        for friend in self.network.successors(node):
            # return friends which edge node->friends was created before the current date
            if (self.network[node][friend][self.EDGE_CREATE_TIME] <= current_date):
                friends.append(friend)
        return friends

    def num_friends(self, node, current_date):
        return len(self.friends(node, current_date))

    def date_to_step(self, timestamp):
        if timestamp < self.start_date:
            return 0
        return (timestamp - self.start_date) // self.intervals
