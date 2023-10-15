import pickle


with open('data/users.pkl', 'rb') as fp:
    users = pickle.load(fp)
    print('users loaded successfully from file')
    
with open('data/activities.pkl', 'rb') as fp:
    activities = pickle.load(fp)
    print('activities loaded successfully from file')

with open('data/track_points.pkl', 'rb') as fp:
    track_points = pickle.load(fp)
    print('track points loaded successfully from file')