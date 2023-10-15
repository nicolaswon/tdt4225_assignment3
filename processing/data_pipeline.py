import pandas as pd
from processing.data_processing import *

def pipeline(data_path):
    track_points_raw = get_track_points(data_path, process_track_points)
    track_points_df = clean_track_points(track_points_raw)

    users_df = get_users(data_path)
    labels_df = get_labels(data_path, get_users)

    removed_users = find_removed_users(track_points_df, users_df)

    users_table = make_user_df(users_df, removed_users)
    activities_table = make_activity_df(track_points_df, labels_df)
    track_points_table = make_track_point_df(track_points_df, activities_table)

    users_dict = make_user_dict(users_table, activities_table)
    activities_idct = make_activity_dict(activities_table)
    track_points_dict = make_track_point_dict(track_points_table)
    
    return users_dict, activities_idct, track_points_dict
