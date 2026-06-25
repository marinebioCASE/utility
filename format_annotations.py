import pandas as pd
import pathlib
import standardizers_biodcase

renaming = {'Bm.Ant-A': 'bma', 
            'Bm.Ant-B': 'bmb', 
            'Bm.Ant-Z': 'bmz', 
            'Bp.20': 'bp20',
            'Bp.20Plus': 'bp20plus', 
            'Bp.Downsweep': 'bpd', 
            'UnsureBlueOrFin.Downsweep': 'fm'}

# start_datetime	end_datetime	duration


raven_renaming_columns = {'Low Freq (Hz)': 'low_frequency',
                          'High Freq (Hz)': 'high_frequency', 
                          'Begin File': 'filename', 
                          'Delta Time (s)': 'duration'}


def convert_raven_to_biodcase(raven_folder_path, output_path):
    station_name = raven_folder_path.name
    selections = None
    for txt_path in raven_folder_path.glob('*.txt'): 
        if (station_name in txt_path.name) and ('.selections' in txt_path.name): 
            for call_key in renaming.keys(): 
                if call_key in txt_path.name: 
                    call_name = renaming[call_key]
                    selections_call_type = pd.read_table(txt_path)
                    selections_call_type['annotation'] = call_name
                    if selections is None:
                        selections = selections_call_type
                    else: 
                        selections = pd.concat([selections, selections_call_type], ignore_index=True)
                    continue
    selections['dataset'] = station_name.lower()
    selections['annotator'] = 'unknown'
    selections_formatted = format_selections(selections)
    selections_formatted.to_csv(output_path.joinpath(station_name.lower() + '.csv'))
    

def format_selections(selections): 
    selections = selections.rename(columns=raven_renaming_columns)
    selections = selections.loc[selections.duration > 0]
    selections_filename_str = selections.filename.str.replace('.wav', '')
    filename_datetime = pd.to_datetime(selections_filename_str, format='%Y%m%d_%H%M%S') 
    selections.filename = filename_datetime.dt.strftime(date_format='%Y-%m-%dT%H-%M-%S_%f') + '.wav'
    selections.filename = selections.filename.str.replace('000000.wav', '000.wav')
    fs = (selections['End File Samp (samples)'] - selections['Beg File Samp (samples)']) / selections.duration

    selections['start_datetime'] = filename_datetime + pd.to_timedelta(selections['Beg File Samp (samples)'] / fs, unit='seconds')
    selections['end_datetime'] = selections['start_datetime'] + pd.to_timedelta(selections.duration, unit='seconds')

    
    selections['start_datetime'] = selections['start_datetime'].apply(lambda x: x.isoformat(timespec='microseconds'))
    selections['end_datetime'] = selections['end_datetime'].apply(lambda x: x.isoformat(timespec='microseconds'))
    
    return selections[['dataset',
                       	'filename',
                        'annotation',
                        'annotator',
                        'low_frequency',
                        'high_frequency',
                        'start_datetime',
                        'end_datetime',
                        'duration'
                        ]]



if __name__ == "__main__": 
    folder_raven_tables = pathlib.Path(input('Where is the folder with the original Raven tables?'))
    output_path = pathlib.Path(input('Where should we store the resulting csv file?'))
    convert_raven_to_biodcase(folder_raven_tables, output_path)