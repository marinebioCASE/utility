import pandas as pd
import pathlib
import soundfile as sf
import datetime


def check_annotations_folder(folder_path):
    total_bad_selections = pd.DataFrame()
    wav_files_duration = {}
    for wav_file_path in folder_path.joinpath('raw').glob('*/*.wav'):
        wav_file = sf.SoundFile(wav_file_path)
        wav_files_duration[wav_file_path.parent.name + '_' + wav_file_path.name] = datetime.timedelta(seconds=wav_file.frames / wav_file.samplerate)
    for annotation_file in folder_path.joinpath('annotations').glob('*.csv'):
        selections = pd.read_csv(annotation_file, parse_dates=['start_datetime', 'end_datetime'])
        selections['start_datetime_wav'] = pd.to_datetime(selections['filename'].apply(lambda y: y.split('.')[0]),
                                                          format='%Y-%m-%dT%H-%M-%S_%f')
        selections['start_datetime_wav'] = selections['start_datetime_wav'].dt.tz_localize('UTC')
        selections['end_datetime'] = selections['end_datetime'].dt.tz_localize('UTC')
        selections['start_datetime'] = selections['start_datetime'].dt.tz_localize('UTC')

        selections['end_datetime_wav'] = None
        for (dataset_name, wav_name), wav_selections in selections.groupby(['dataset', 'filename']):
            selections.loc[wav_selections.index, 'end_datetime_wav'] = wav_selections['start_datetime_wav'] + \
                                                                       wav_files_duration[dataset_name + '_' + wav_name]
        selections['end_datetime_wav'] = pd.to_datetime(selections['end_datetime_wav'])

        bad_selections = selections.loc[(selections['start_datetime'] < selections['start_datetime_wav']) | (
                selections['end_datetime'] > selections['end_datetime_wav']) | (
                                                    selections['start_datetime'] > selections['end_datetime_wav']) | (
                                                    selections['end_datetime'] < selections['start_datetime_wav'])]

        print(annotation_file, len(bad_selections))
        total_bad_selections = pd.concat([total_bad_selections, bad_selections], ignore_index=True)
    total_bad_selections['is_precision_prob'] = (total_bad_selections['end_datetime'] - total_bad_selections['end_datetime_wav']) < pd.to_timedelta(1, unit='seconds')
    total_bad_selections.to_csv(folder_path.joinpath('bad_annotations.csv'))


check_folder = input('Where is the folder to be checked? (needs to have an annotations folder inside)')
check_annotations_folder(pathlib.Path(check_folder))
