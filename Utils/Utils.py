import pickle
from scipy.spatial.distance import cosine
from pymongo import MongoClient


def date_to_step(timestamp, start_date, intervals):
    if timestamp < start_date:
        return 0
    return (timestamp - start_date) // intervals
def detect_type(file):
    assert type(file) == str,'file must be string!'
    if file[-3:-1] == '.p':
        return 'p'
    elif file[-5:-1] == '.json':
        return 'json'


def make_userid(file):
    type = detect_type(file)
    if type == "p":
        dat = pickle.load(open(file),'rb')

def topical_similarity(user1, user2):
        # return cosine_similarity(user1,user2)  ## Error
        return 1 - cosine(user1, user2)

def read_users(user_file,type='p'):
    assert any(type in i for i in ['p','csv']) , "Only support csv and pickle file."
    if type == 'csv':
        with open(user_file, 'rb') as f:
            users = map(int, f.readlines())
        return users
    elif type == 'p':
        with open(user_file,'rb') as f:
            return pickle.load(f)



def get_mongo_connection(host="127.0.0.", port=27017, db_name="stream_store",no=1):
    host = host + str(no)
    return MongoClient(host=host, port=port)[db_name]


### For Multi-Processing
def divide_work(num,coren):
    """

    :param num      :   Length of Samples
    :param coren    :   core number
    :return         :   range list
                     ：  if we have 9998 samples, then it will divided by [range(0,2500),range(2500,5000),
                                                                            range(5000,7500),range(7500,9998)]
    """
    part = []
    rest = num % coren
    o = int((num - rest)/coren)
    temp = 0
    for i in range(coren):
        if i == (coren-1):
            temp = rest
        part.append(range(i*o,i * o + o + temp ) )
    return part

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out