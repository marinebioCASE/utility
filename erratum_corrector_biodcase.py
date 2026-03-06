import os
import sys
import pandas as pd
import logging
from tqdm import tqdm
from datetime import datetime, timedelta
import librosa
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from standardizers_biodcase import filename2datetime, iso2datetime, datetime2iso

splits = ['train', 'validation'] # if root is biodcase_development_set/
# splits = ['evaluation'] # if root is biodcase_evaluation_set/


now = datetime.now().strftime('%m-%dT%H-%M')
list_annot = ['bma', 'bmb', 'bmz', 'bmd', 'bp20', 'bp20plus', 'bpd', 'bmbpd'] # drop 0.286 > annot for the labels of interest 
                                                                              # (some "unknown" are < 0.286 but we don't use this label
                                                                              # -> we don't mind keep them as it ?)

for s in splits:
    annot_path = os.path.join(s, 'annotations')
    audio_path = os.path.join(s, 'audio')
    list_annot_files = [f for f in os.listdir(annot_path) if f.endswith('.csv')]

    for file in list_annot_files:
        sub_name = file.replace('.csv', '')
        audio_path_sub = os.path.join(audio_path, sub_name)
        df = pd.read_csv(os.path.join(annot_path, file))

        for i in tqdm(range(df.shape[0])):
            file_name = df.loc[df.index[i], 'filename']
            start_file_dt = filename2datetime(file_name)

            duration_sec = librosa.get_duration(path=os.path.join(audio_path_sub, file_name))
            end_file_dt = start_file_dt + timedelta(seconds=duration_sec)

            # start_annot_dt = iso2datetime(df.loc[df.index[i], 'start_datetime'])
            end_annot_dt = iso2datetime(df.loc[df.index[i], 'end_datetime'])

            df.loc[df.index[i], 'end_datetime'] = datetime2iso(min(end_annot_dt, end_file_dt))  # cut what exceeds

        sub_df_annot = df[df['annotation'].isin(list_annot)].copy()
        sub_df_annot['start_datetime'] = pd.to_datetime(sub_df_annot['start_datetime'])
        sub_df_annot['end_datetime'] = pd.to_datetime(sub_df_annot['end_datetime'])
        sub_df_annot['duration'] = (sub_df_annot['end_datetime'] - sub_df_annot['start_datetime']).dt.total_seconds()
        sub_df_annot = sub_df_annot[sub_df_annot['duration'] >= 0.286]  # min duration for [bmabz, dwnswps, bp20]
        sub_df_annot.drop(columns=['duration'], inplace=True)
        sub_df_annot['start_datetime'] = sub_df_annot['start_datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S.%f')  # reformat
        sub_df_annot['end_datetime'] = sub_df_annot['end_datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S.%f')  # reformat

        sub_df_not_annot = df[~ df['annotation'].isin(list_annot)].copy()
        df = pd.concat([sub_df_annot, sub_df_not_annot], ignore_index=True)

        df.to_csv(os.path.join(annot_path, f'{sub_name}_corrected.csv'), index=False)