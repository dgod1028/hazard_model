import pickle

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
