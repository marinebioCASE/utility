from datetime import datetime

##################################################
#                TIME
##################################################
# TODO prendre en charge pd.Series() avec dt.strftime()

def filename2iso(filename : str) -> str:
    filename = filename[:-4] if '.wav' in filename else filename
    dt = datetime.strptime(filename, '%Y-%m-%dT%H-%M-%S_%f')
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-2]

def iso2filename(iso_ts: str, with_wav: bool = True) -> str:
    dt = datetime.strptime(iso_ts, '%Y-%m-%dT%H:%M:%S.%f')
    base = dt.strftime('%Y-%m-%dT%H-%M-%S_%f')[:-3]
    return f'{base}.wav' if with_wav else base

def iso2datetime(iso: str) -> datetime:
    return datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%f')

def filename2datetime(filename: str) -> datetime:
    filename = filename[:-4] if '.wav' in filename else filename
    return datetime.strptime(filename, '%Y-%m-%dT%H-%M-%S_%f')

def datetime2filename(dt: datetime, with_wav=True) -> str:
    base = dt.strftime('%Y-%m-%dT%H-%M-%S_%f')[:-3]
    return f'{base}.wav' if with_wav else base

def datetime2iso(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
