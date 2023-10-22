import pickle


with open('data/usersv2.pkl', 'rb') as fp:
    users = pickle.load(fp)
    print('users loaded successfully from file')
    
with open('data/activitiesv2.pkl', 'rb') as fp:
    activities = pickle.load(fp)
    print('activities loaded successfully from file')

with open('data/track_pointsv2.pkl', 'rb') as fp:
    track_points = pickle.load(fp)
    print('track points loaded successfully from file')