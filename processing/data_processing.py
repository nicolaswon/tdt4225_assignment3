import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor
from processing.helpers import process_track_points, find_removed_users, haversine
from bson import ObjectId
import numpy as np

from collections.abc import Callable

MAX_ALLOWED_ROWS = 2506

def get_track_points(data_path, process_func):
    """
        Get track points from the dataset
    """
    data_frames = []
    data_path = f"{data_path}/Data"
    user_folders = os.listdir(data_path)
    user_folders.sort()

    with ThreadPoolExecutor() as executor:
        futures = []
        for user in user_folders:
            activity_dir_path = os.path.join(data_path, user)
            if not os.path.isdir(activity_dir_path):
                continue
            for trajectory_dir in os.listdir(activity_dir_path):
                trajectory_dir_path = os.path.join(activity_dir_path, trajectory_dir)

                if not os.path.isdir(trajectory_dir_path):
                    continue

                for activity_file in os.listdir(trajectory_dir_path):
                    if not activity_file.endswith('.plt'):
                        continue

                    file_path = os.path.join(trajectory_dir_path, activity_file)
                    futures.append(executor.submit(process_func, file_path, user, activity_file[:-4],MAX_ALLOWED_ROWS))

        for future in futures:
            data_frames.extend(future.result())

    final_df = pd.DataFrame(data_frames)
    return final_df

def clean_track_points(track_points_df: pd.DataFrame):
    """
        Convert columns to the correct type and format
    """
    track_points_df['user'] = track_points_df['user'].astype(str).str.zfill(3)
    track_points_df["activity"] = track_points_df['activity'].astype(str)
    track_points_df["lat"] = track_points_df['lat'].astype(float)
    track_points_df["lon"] = track_points_df['lon'].astype(float)
    track_points_df["altitude"] = track_points_df['altitude'].astype(float)
    track_points_df["date_days"] = track_points_df['date_days'].astype(float)
    track_points_df["time_string"] = track_points_df["time_string"].str.replace('\n', '')
    track_points_df["date_time"] = track_points_df["date_string"] + " " + track_points_df["time_string"]
    track_points_df['date_time'] = pd.to_datetime(track_points_df['date_time'], format='%Y-%m-%d %H:%M:%S')
    
    results_df = track_points_df.drop(['date_string', 'time_string'], axis=1)
    return results_df

def get_users(data_path: str): 
    """
        Get users from the dataset, and check for labels
    """
    directories_data = os.listdir(f'{data_path}/Data')
    labeled_ids_path = f'{data_path}/labeled_ids.txt'
    
    with open(labeled_ids_path, "r") as file:
        lines = file.readlines()
    ids = [line.strip().split()[0] for line in lines]

    df= pd.DataFrame({"id": [user_id for user_id in directories_data if len(user_id) == 3]})
    labeled_ids_df = pd.DataFrame({"LabelID":ids})

    merged_df = pd.merge(df, labeled_ids_df, left_on="id", right_on="LabelID", how = "left")
    merged_df["has_labels"] = merged_df["LabelID"].notna()
    merged_df.drop("LabelID", axis=1, inplace=True)

    return merged_df

def get_labels(data_path: str, get_users_func: Callable): 
    """
        Function for getting the content in labels.txt for those user which have has_label = True
    """
    labels_df = pd.DataFrame(columns=["user_id","start_date_time", "end_date_time", "transportation_mode"])
    user_df = get_users_func(data_path)
    folders_with_labels = user_df[user_df["has_labels"]]
    
    for _, row in folders_with_labels.iterrows(): 
        folder_id = row["id"]
    
        labels_file_path = os.path.join(f"{data_path}/Data", folder_id, "labels.txt").replace("\\", "/")
        

        if os.path.isfile(labels_file_path): 
            labels_data = pd.read_csv(labels_file_path, sep = "\t", names=['start_date_time', 'end_date_time', 'transportation_mode'], skiprows=1)
            labels_data["user_id"] = folder_id
            labels_df = pd.concat([labels_df, labels_data], ignore_index=True)

    # Formating from string to datetime object so comparisons can be made. Those invalid rows have NaT (Not a Time)
    labels_df['start_date_time'] = pd.to_datetime(labels_df['start_date_time'], format="%Y/%m/%d %H:%M:%S", errors='coerce')
    labels_df['end_date_time'] = pd.to_datetime(labels_df['end_date_time'], format="%Y/%m/%d %H:%M:%S", errors='coerce')

    return labels_df

def find_start_end(track_points_df): 
    grouped = track_points_df.groupby(["user", "activity"])

    users = []
    activities = []
    start_date_times = []
    end_times = []

    for (user, activity), grouped_df in grouped: 
        earliest_time = grouped_df["date_time"].min()
        latest_time = grouped_df["date_time"].max()

        users.append(user)
        activities.append(activity)
        start_date_times.append(earliest_time)
        end_times.append(latest_time)

    result_df = pd.DataFrame({
        'user_id': users,
        'activity': activities,
        'start_date_time': start_date_times,
        'end_date_time': end_times
    })

    return result_df

def process_dataframe(input_df: pd.DataFrame, distance_func, std_multiplier=3):
    df = input_df.copy()
    df = df.drop_duplicates(subset=['activity_id', 'date_time'], keep='last')
    df.set_index(['activity_id','date_time'], inplace=True)
    df['prev_lat'] = df.groupby('activity_id')['lat'].shift(1)
    df['prev_lon'] = df.groupby('activity_id')['lon'].shift(1)

    df['distance_to_prev'] = df.apply(lambda row: distance_func(row['lon'], row['lat'], row['prev_lon'], row['prev_lat']), axis=1)

    df.drop(columns=['prev_lat', 'prev_lon'], inplace=True)

    df['mean_distance'] = df.groupby('activity_id')['distance_to_prev'].transform('mean')
    df['std_distance'] = df.groupby('activity_id')['distance_to_prev'].transform('std')

    filtered_df = df[
        (df['distance_to_prev'] >= (df['mean_distance'] - std_multiplier * df['std_distance'])) &
        (df['distance_to_prev'] <= (df['mean_distance'] + std_multiplier * df['std_distance']))
    ]

    filtered_df.drop(columns=['mean_distance', 'std_distance', 'distance_to_prev'], inplace=True)
    filtered_df.reset_index(inplace=True)

    return filtered_df

# Final output step

def make_user_df(user_df, exclude_ids: list):
    user_df = user_df[~user_df["id"].isin(exclude_ids)]
    user_df.rename(columns={'id': '_id'}, inplace=True)
    return user_df

def make_activity_df(track_points_df, labels_df): 
    columns = ["user_id", "start_date_time", "end_date_time"]
    start_end_df = find_start_end(track_points_df)
    merged_df = pd.merge(start_end_df, labels_df, on=columns, how="left")
    
    merged_df["id"] = merged_df["activity"] + merged_df["user_id"]
    result_df = merged_df.drop(["activity"], axis=1)

    result_df = result_df.drop_duplicates(subset=['id'], keep='last')
    result_df.rename(columns={'id': '_id'}, inplace=True)
    result_df['transportation_mode'] = result_df['transportation_mode'].where(pd.notna(result_df['transportation_mode']), None)
    
    return result_df

def make_track_point_df(track_points_df, activities_df): 
    track_points_df["activity_id"] = track_points_df["activity"] + track_points_df["user"]
    int_df = track_points_df.drop(["activity", "user"], axis=1)
    cleaned_df = process_dataframe(int_df, haversine)
    result_df = cleaned_df.merge(activities_df, left_on=['activity_id'], right_on=['_id'])
    result_df.sort_values(['activity_id', 'date_time'], inplace=True)
    result_df['prev_date_time'] = result_df.groupby('activity_id')['date_time'].shift(1)
    result_df['prev_date_time'].replace({np.nan: None}, inplace=True)
    result_df = result_df[['user_id', 'activity_id', 'lat', 'lon', 'altitude', 'date_days', 'date_time', 'transportation_mode', 'prev_date_time']]
    return result_df

def make_user_dict(user_table, activities_table):
    user_dict = user_table.to_dict('records')
    [user.update({'activities': list(activities_table.loc[activities_table['user_id'] == user['_id'], '_id'].unique())}) for user in user_dict]
    return user_dict

def make_activity_dict(activity_table):
    activity_dict = activity_table.to_dict('records')
    return activity_dict

def make_track_point_dict(track_point_table):
    track_point_table['location'] = track_point_table.apply(lambda row: {"type": "Point", "coordinates": [row['lon'], row['lat']]}, axis=1)
    track_point_table.drop(columns=['lon', 'lat'], inplace=True)
    track_point_dict = track_point_table.to_dict('records')
    return track_point_dict