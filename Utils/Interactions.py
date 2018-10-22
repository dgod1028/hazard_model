"""
helper methods to get all indices
input : interactions file json or pickel
 """
import pickle
import json
class Interaction:
    def __init__(self, file_name, type='p'):
        '''
        :param file_name: file containing interactions
        :param type: "json" or "p"
        '''
        self.interactions = self.load_file(file_name, type)
        # self.memoise = dict()
    def retweet_jaccard(self, user1, user2):
        key = (user1, user2)
        # if(key  in self.memoise):
        #     return self.memoise[key]
        user1_retweet_set = set(self.interactions[int(user1)]['retweets'].keys())

        user2_retweet_set = set(self.interactions[int(user2)]['retweets'].keys())
        jac = Interaction.jaccard(user1_retweet_set, user2_retweet_set)
        # self.memoise[key] = jac
        return jac
    def interaction_count(self, user1, user2):
        '''
         :param user1: source user
        :param user2: destination user
        :return: count of interaction from user1 to user2
        '''
        all_interactions = self.interactions[int(user1)]['interactions']
        s_user2 = str(user2)
        if s_user2 in all_interactions:
            return all_interactions[s_user2]
        else:
            return 0
    def load_file(self,filename, type):
        if type == 'p':
            interactions = pickle.load(open(filename, 'rb'))
        else:
            interactions = json.load(open(filename, 'r'))
        return interactions

    def jaccard(a, b):
            if len(a) == len(b) == 0:
                return 0
            else:
                return float(len(a & b)) / len(a | b)