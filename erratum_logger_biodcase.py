import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
import logging
from tqdm import tqdm
from datetime import datetime, timedelta
from standardizers_biodcase import filename2datetime, iso2datetime
import librosa

splits = ['train', 'validation'] # if root is biodcase_development_set/
# splits = ['evaluation'] # if root is biodcase_evaluation_set/

now = datetime.now().strftime('%m-%dT%H-%M')

logging.basicConfig(
    filename=f'/home/lucie/Bureau/tez/code/tasks/eda/phd/log_annotations_errors_{now}.txt', # customize log name here
    filemode='w',
    level=logging.INFO,
    format='%(message)s'
)

for s in splits:
    annot_path = os.path.join(s, 'annotations')
    audio_path = os.path.join(s, 'audio')
    list_annot_files = [f for f in os.listdir(annot_path) if f.endswith('.csv')]

    for file in list_annot_files:
        sub_name = file.replace('.csv', '')
        audio_path_sub = os.path.join(audio_path, sub_name)

        df = pd.read_csv(os.path.join(annot_path, file))
        new_line = False

        for i in tqdm(range(df.shape[0])):
            file_name = df.loc[df.index[i], 'filename']
            start_file_dt = filename2datetime(file_name)

            duration_sec = librosa.get_duration(path=os.path.join(audio_path_sub, file_name))
            end_file_dt = start_file_dt + timedelta(seconds=duration_sec)

            start_annot_dt = iso2datetime(df.loc[df.index[i], 'start_datetime'])
            end_annot_dt = iso2datetime(df.loc[df.index[i], 'end_datetime'])

            if end_annot_dt > end_file_dt:  # check the boxes that exceed file length
                new_line = True
                diff = end_annot_dt - end_file_dt
                total_seconds = diff.total_seconds()
                hours, rem = divmod(total_seconds, 3600)
                minutes, rem = divmod(rem, 60)
                seconds = int(rem)
                milliseconds = int((rem - seconds) * 1000)
                logging.info(
                    f'{sub_name} | {file_name} | annotation starting at {start_annot_dt} exceeds file end by {int(minutes):02d} min {seconds:02d} sec {milliseconds:03d} milisec')

            if start_annot_dt > end_annot_dt:  # check that no end_dt BEFORE start_dt (none)
                new_line = True
                logging.info(f'{sub_name} | {file_name} | start_annot > end_annot at {i} (iloc)')

        if new_line:
            logging.info('\n')

