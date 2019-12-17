import json
from Variables.Variable import Variable
from Utils.Utils import *
import math
import os

"""
    XSentiment for X4Positive, X5Neutral, X6Negative
"""

class XSentiment(Variable):
    POSITIVE = 1
    NEUTRAL = 0
    NEGATIVE = -1

    def __init__(self, g, json_file, sentiment_category):
        assert sentiment_category in [self.POSITIVE, self.NEUTRAL, self.NEGATIVE], "Sentiment category must be -1/0/1"
        self.sentiment_category = sentiment_category

        if sentiment_category == self.POSITIVE:
            super().__init__("PositiveSentiment")
        elif sentiment_category == self.NEUTRAL:
            super().__init__("NeutralSentiment")
        else:
            super().__init__("NegativeSentiment")

        self.network = g
        if sentiment_category == -1:
            n = "negative"
        elif sentiment_category == 0:
            n = "neutral"
        else:
            n = "positive"
        self.sentiment_file = "data/sentiment_%s.p" % sentiment_category

        if os.path.isfile(self.sentiment_file):
            self.sentiment = pickle.load(open(self.sentiment_file,"rb"))
        else:
            self.sentiment = self.parse_sentiment_data_by_step(
                    json.load(open(json_file)),
                    self.network.start_date,
                    self.network.stop_step,
                    self.network.intervals)



    def get_covariate(self, node, current_date, nonadopted, step):
        """
        Return number of specific sentiment a node received from its adopted neighbor.
        At step 0, the value should be 0, since no neighbor is adopted.

        :param node: 
        :param current_date: 
        :param nonadopted: 
        :return:                sentiment varialbe of node at current_date 
        """
        step = date_to_step(current_date, self.network.start_date, self.network.intervals)
        if step == 0:
            return 0.0
        num_sentiment = 0.0
        # adopted_neighbors = 0.0
        for neighbor in self.network.friends(node, current_date):
            if neighbor in nonadopted:
                continue
            else:
                # adopted_neighbors += 1
                num_sentiment += self.sentiment[str(neighbor)][step-1]

        # # return self.sentiment[node][step]
        # if adopted_neighbors == 0:
        return math.log(num_sentiment+1)
        # else:
        #     return num_sentiment / adopted_neighbors

    # def parse_sentiment(self, json_data, start_date, stop_step, intervals, debug=False):
    #     """
    #     Combine the raw sentiment data measure in second into data measure by step length(cumulative).
    #     :return: Dictionary format data
    #     {
    #         "User1": [
    #             num_positive_tweets,            # Step 0
    #             num_positive_tweets,            # Step 1
    #             num_positive_tweets,            # Step 2
    #             num_positive_tweets,            # Step 3
    #         ],
    #         "User2": [
    #             num_positive_tweets,
    #             num_positive_tweets,
    #             num_positive_tweets,
    #             num_positive_tweets,
    #         ]
    #
    #     }
    #     """
    #     sentiment_data = self.parse_sentiment_data_by_step(json_data, start_date, stop_step, intervals)
    #     average_data = {}
    #     for user_id, data_by_weeks in sentiment_data.items():
    #         average_data[user_id] = []
    #         for week in data_by_weeks:
    #             if week == [] and len(average_data[user_id]) == 0:
    #                 average_data[user_id].append(0)
    #             elif week == []:
    #                 average_data[user_id].append(average_data[user_id][-1])
    #             else:
    #                 average_data[user_id].append(sum(week) / len(week))
    #     return average_data

    def parse_sentiment_data_by_step(self, json_data, start_date, stop_step, intervals, debug=False):
        """
            Combine the raw sentiment data measure in second into data measure by step length.
            :return: Dictionary format data
            {
                "User1": {
                    num_positive_tweets,            # Step 0
                    num_positive_tweets,            # Step 1
                    num_positive_tweets,            # Step 2
                    num_positive_tweets,            # Step 3
                },
                "User2": {
                    num_positive_tweets,
                    num_positive_tweets,
                    num_positive_tweets,
                    num_positive_tweets,
                }
            }
        """
        if debug:
            print("start date: {}".format(start_date))

        sentiment_data = {}
        for user_id, messages in json_data.items():
            sentiment_data[user_id] = [0 for _ in range(stop_step + 1)]
            for date, sentiment_value in messages.items():
                if int(sentiment_value) != self.sentiment_category:
                    continue
                step = min(stop_step, date_to_step(int(date), start_date, intervals))
                sentiment_data[user_id][step] += 1

                if debug:
                    print("{}({}): {}".format(date, step, sentiment_value))

        # Cumulative values
        for user_id in sentiment_data.keys():
            for index in range(1, stop_step+1):
                sentiment_data[user_id][index] += sentiment_data[user_id][index-1]

        if debug:
            for k, v in sentiment_data.items():
                print("{} {}".format(k, v))
        pickle.dump(sentiment_data,open(self.sentiment_file,"wb"))
        return sentiment_data