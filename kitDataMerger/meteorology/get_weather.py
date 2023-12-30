import os

import requests as req
from datetime import datetime, timedelta
import pytz
import pandas as pd
from requests.exceptions import ConnectionError
import tkinter as tk
from tkinter.messagebox import showerror
import numpy as np
import geopy.distance
import time
from typing import List
import re
import logging
import dotenv
import certifi

# Load environment variables from a .env file
headers = {'Authorization': os.environ.get("API_KEY")}

# Set API key for authorization
dotenv.load_dotenv(dotenv.find_dotenv())

def distance(station, x, y):
    """
    Calculate the geodesic distance between a given station and coordinates (x, y).

    Parameters:
    - station: Dictionary containing station information with 'location' key.
    - x: Latitude of the target coordinates.
    - y: Longitude of the target coordinates.

    Returns:
    Geodesic distance in kilometers.
    """
    try:
        return geopy.distance.geodesic((x, y), (station['location']['latitude'], station['location']['longitude'])).km
    except TypeError:
        return 999999


def get_timezone(d: datetime):
    """
    Get the timezone information for a given datetime object.

    Parameters:
    - d: Datetime object.

    Returns:
    Timezone information as a string.
    """
    israel = pytz.timezone('Israel').localize(d).strftime('%Y/%m/%d  %H:%M:%S %Z/%z').split('  ')
    return '+02:00' if 'IST' in israel[1] else '+03:00'


def round_timestamp(d: datetime, tz: str):
    """
    Round the timestamp of a given datetime object.

    Parameters:
    - d: Datetime object.
    - tz: Timezone information.

    Returns:
    Rounded timestamp as a formatted string.
    """
    return f'{d.year}-{str(d.month).zfill(2)}-{str(d.day).zfill(2)}' \
           f'T{str(d.hour).zfill(2)}:{str(round(d.minute, 2)).zfill(2)}:00{tz}'


def next_day(d: datetime):
    """
    Calculate the datetime for the next day.

    Parameters:
    - d: Datetime object.

    Returns:
    Datetime object for the next day.
    """
    return d + timedelta(days=1)


def get_stations_json():
    """
    Retrieve JSON data containing information about stations.

    Returns:
    JSON data with station information.
    """
    return get_response_json(f"https://api.ims.gov.il/v1/envista/stations")


def get_response_json(url, params=None):
    """
    Make a GET request to the specified URL and retrieve JSON data.

    Parameters:
    - url: URL for the GET request.
    - params: Optional parameters for the request.

    Returns:
    JSON data from the response.
    """
    response = req.get(url, params=params, headers=headers, verify=certifi.where())
    response.raise_for_status()
    return response.json()


def parse_cord(d):
    """
    Parse a coordinate string into a list of float values.

    Parameters:
    - d: Coordinate string.

    Returns:
    List of float values representing coordinates.
    """
    return [float(c.strip(' ')) for c in d.split(',' if ',' in d else ' ')]


def sort_samples(samples, progress_var: tk.DoubleVar, percentage_label: tk.Label, status_label: tk.Label):
    """
    Sort samples based on station distances.

    Parameters:
    - samples: List of samples with station information.
    - progress_var: Tkinter variable for tracking progress.
    - percentage_label: Tkinter label for displaying progress percentage.
    - status_label: Tkinter label for displaying status messages.

    Returns:
    Dictionary with samples grouped by station ID.
    """
    status_label.config(text="Sorting Samples")
    number_of_samples = len(samples)
    progress_counter = 0
    sample_by_stations = {}
    for sample in samples:
        if pd.isnull(sample['TD']) or pd.isnull(sample['TDmin']) or pd.isnull(sample['TDmax']) or pd.isnull(
                sample['TG']) or pd.isnull(sample['WSmax']) or pd.isnull(sample['WDmax'])\
                or pd.isnull(sample['WS']) or pd.isnull(sample['WD']) or pd.isnull(sample['STDwd'])\
                or pd.isnull(sample['Grad']) or pd.isnull(sample['NIP']) or pd.isnull(sample['DiffR'])\
                or pd.isnull(sample['RH']) or pd.isnull(sample['Rain']):
            if len(sample['stations']):
                station_id = sample['stations'][0]['id']
                if station_id not in sample_by_stations.keys():
                    sample_by_stations[station_id] = []
                sample_by_stations[station_id].append(sample)
        progress_counter += 1
        progress = (progress_counter / number_of_samples) * 100
        progress_var.set(progress)
        percentage_label.config(text=(('%.2f ' % progress) + '%'))
    return sample_by_stations

def is_valid_date(date_string):
    """
    Check if a date string is in a valid format (MM/DD/YYYY).

    Parameters:
    - date_string: Date string.

    Returns:
    True if the date is in a valid format, False otherwise.
    """
    pattern = r"^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/(19|20)\d{2}$"
    return re.match(pattern, date_string) is not None

def convert_american_date_to_normal(date: str):
    """
    Convert an American date format (MM/DD/YYYY) to a normal date format (DD/MM/YYYY).

    Parameters:
    - date: American date string.

    Returns:
    Date string in normal format.
    """
    date_split = date.split('/')
    return f'{date_split[1]}/{date_split[0]}/{date_split[2]}'


def parse_table(df: pd.DataFrame, stations, radius, progress_var: tk.DoubleVar, percentage_label: tk.Label, status_label: tk.Label):
    """
    Parse table data and extract relevant information.

    Parameters:
    - df: Pandas DataFrame containing table data.
    - stations: List of environmental stations.
    - radius: Maximum distance for station inclusion.
    - progress_var: Tkinter variable for tracking progress.
    - percentage_label: Tkinter label for displaying progress percentage.
    - status_label: Tkinter label for displaying status messages.

    Returns:
    List of dictionaries representing parsed samples.
    """
    samples = []
    status_label.config(text="Parsing Table")
    rows = df.iterrows()
    number_of_rows = len(df.index)
    progress_counter = 0
    for index, row in rows:
        dateTime = str(row['Date']).split()
        if (not type(dateTime) is List or len(dateTime) == 1):
            time = "12:00:00"
            date = dateTime[0]
        else:
            time = dateTime[1]
            date = dateTime[0]
        
        if not is_valid_date(date):
            logging.error(f"Date in Kit ID {row['Kit ID']} is not valid: {date}")
            continue
        else:
            date = convert_american_date_to_normal(date)
        date_split = date.split("/")
        time_split = time.split(':')
        dt = datetime(
            year=int(date_split[2]),
            month=int(date_split[1]),
            day=int(date_split[0]),
            hour=int(time_split[0]),
            minute=int(time_split[1]),
            second=int(time_split[2])
        )
        if not pd.isna(row['Coordination']):
            cord = parse_cord(row['Coordination'])
        data = {
            'index': index,
            'date': f'{dt.year}/{dt.month}/{dt.day}',
            'timestamp': round_timestamp(dt, get_timezone(dt)),
            'cord': cord,
            'TD': row['TD'],
            'TG': row['TG'],
            'TDmin': row['TDmin'],
            'TDmax': row['TDmax'],
            'WSmax': row['WSmax'],
            'WDmax': row['WDmax'],
            'WS': row['WS'],
            'WD': row['WD'],
            'STDwd': row['STDwd'],
            'Grad': row['Grad'],
            'NIP': row['NIP'],
            'DiffR': row['DiffR'],
            'RH': row['RH'],
            'Rain': row['Rain'],
            'stations': []
        }
        for station in stations:
            dis = distance(station, cord[0], cord[1])
            if dis <= radius:
                data['stations'].append(dict(id=station['stationId'], dis=dis))
        data['stations'].sort(key=lambda a: a.get('dis'))
        samples.append(data)
        progress_counter += 1
        progress = (progress_counter / number_of_rows) * 100
        progress_var.set(progress)
        percentage_label.config(text=(('%.2f ' % progress) + '%'))
    return samples


def update_weather(filepath, radius, progress_var: tk.DoubleVar, percentage_label: tk.Label, status_label: tk.Label):
    """
    Update weather information for samples in a CSV file.

    Parameters:
    - filepath: Path to the CSV file containing samples.
    - radius: Maximum distance for station inclusion.
    - progress_var: Tkinter variable for tracking progress.
    - percentage_label: Tkinter label for displaying progress percentage.
    - status_label: Tkinter label for displaying status messages.

    Returns:
    None
    """
    try:
        stations = get_stations_json()
    except req.exceptions.SSLError:
        status_label.config(text='There was an error with SSL.')
        showerror("SSL error", "There is an error with SSL.")
        return False
        
    df = pd.read_csv(filepath_or_buffer=filepath)
    if 'TD' not in df.columns and 'TDmin' not in df.columns and 'TDmax' not in df.columns and 'TG' not in df.columns and\
        'WSmax' not in df.columns and 'WDmax' not in df.columns and 'WS' not in df.columns and 'WD' not in df.columns \
        and 'STDwd' not in df.columns and 'Grad' not in df.columns and 'NIP' not in df.columns and\
        'DiffR' not in df.columns and 'RH' not in df.columns and 'Rain' not in df.columns:
        columns = ["TD", "TDmin", "TDmax", "TG", "WSmax", "WDmax", "WS", "WD", "STDwd", "Grad", "NIP", "DiffR", "RH", "Rain"]
        for column, index in zip(columns, range(7, 21)):
            df.insert(loc=index, column=column, value=pd.Series([np.nan for _ in range(len(df))]))

    df = df.sort_values(by='Date', ascending=True)
    samples = parse_table(df, stations, radius, progress_var, percentage_label, status_label)
    while True:
        samples = sort_samples(samples, progress_var, percentage_label, status_label)
        status_label.config(text="Getting Information")
        number_of_samples = len(samples)
        progress_counter = 0
        for station_id in samples:
            first_date = samples[station_id][0]['date']
            year_last, month_last, day_last = samples[station_id][-1]['date'].split('/')
            last_date = next_day(datetime(year=int(year_last), month=int(month_last), day=int(day_last)))
            params = {
                'from': first_date,
                'to': f'{last_date.year}/{str(last_date.month).zfill(2)}/{str(last_date.day).zfill(2)}'
            }
            try:
                response = req.get(url=f'https://api.ims.gov.il/v1/envista/stations/{station_id}/data', params=params,
                                    headers=headers,
                                    verify=certifi.where())
            except ConnectionError:
                logging.error('Connection error: Converting what I already have...')
                df.to_csv(f"./kitDataMerger/meta_data_final.csv", index=False, encoding="utf-16")
                logging.info(
                    f"The file was saved in the same directory of the original file as"
                    f" \"meta_data_final.csv\"")
                time.sleep(60)
                exit(-1)
            if response.status_code == 200:
                response = response.json()
                for sample in samples[station_id]:
                    if pd.isnull(sample['TD']) or pd.isnull(sample['TDmin']) or pd.isnull(sample['TDmax']) \
                            or pd.isnull(sample['TG']) or pd.isnull(sample['WSmax']) or pd.isnull(sample['WDmax'])\
                            or pd.isnull(sample['WS']) or pd.isnull(sample['WD']) or pd.isnull(sample['STDwd'])\
                            or pd.isnull(sample['Grad']) or pd.isnull(sample['NIP']) or pd.isnull(sample['DiffR'])\
                            or pd.isnull(sample['RH']) or pd.isnull(sample['Rain']):
                        for data in response['data']:
                            if data['datetime'] == sample['timestamp']:
                                for channel in data['channels']:
                                    if (channel['name'] == 'TD' or channel['name'] == 'TDmin' or channel[
                                        'name'] == 'TDmax' or channel['name'] == 'TG' or channel['name'] == 'WSmax'
                                        or channel['name'] == 'WDmax' or channel['name'] == 'WS'
                                        or channel['name'] == 'TG' or channel['name'] == 'WD'
                                        or channel['name'] == 'STDwd' or channel['name'] == 'Grad'
                                        or channel['name'] == 'NIP' or channel['name'] == 'DiffR'
                                        or channel['name'] == 'RH' or channel['name'] == 'Rain')\
                                        and channel['valid']:
                                        sample[channel['name']] = channel['value']
            progress_counter += 1
            progress = (progress_counter / number_of_samples) * 100
            progress_var.set(progress)
            percentage_label.config(text=(('%.2f ' % progress) + '%'))
                
        length = sum([len(samples[station_id]) for station_id in samples])
        status_label.config(text="Updating")
        progress_counter = 0
        for station_id in samples:
            for sample in samples[station_id]:
                df.at[sample['index'], 'TD'] = sample['TD'] if not pd.isnull(sample['TD']) else "__"
                df.at[sample['index'], 'TDmin'] = sample['TDmin'] if not pd.isnull(sample['TDmin']) else "__"
                df.at[sample['index'], 'TDmax'] = sample['TDmax'] if not pd.isnull(sample['TDmax']) else "__"
                df.at[sample['index'], 'TG'] = sample['TG'] if not pd.isnull(sample['TG']) else "__"
                df.at[sample['index'], 'WSmax'] = sample['WSmax'] if not pd.isnull(sample['WSmax']) else "__"
                df.at[sample['index'], 'WDmax'] = sample['WDmax'] if not pd.isnull(sample['WDmax']) else "__"
                df.at[sample['index'], 'WS'] = sample['WS'] if not pd.isnull(sample['WS']) else "__"
                df.at[sample['index'], 'WD'] = sample['WD'] if not pd.isnull(sample['WD']) else "__"
                df.at[sample['index'], 'STDwd'] = sample['STDwd'] if not pd.isnull(sample['STDwd']) else "__"
                df.at[sample['index'], 'Grad'] = sample['Grad'] if not pd.isnull(sample['Grad']) else "__"
                df.at[sample['index'], 'NIP'] = sample['NIP'] if not pd.isnull(sample['NIP']) else "__"
                df.at[sample['index'], 'DiffR'] = sample['DiffR'] if not pd.isnull(sample['DiffR']) else "__"
                df.at[sample['index'], 'RH'] = sample['RH'] if not pd.isnull(sample['RH']) else "__"
                df.at[sample['index'], 'Rain'] = sample['Rain'] if not pd.isnull(sample['Rain']) else "__"
                progress_counter += 1
                progress = (progress_counter / length) * 100
                progress_var.set(progress)
                percentage_label.config(text=(('%.2f ' % progress) + '%'))

        empty_samples = []
        status_label.config(text="Collecting samples that haven't been updated")
        length = sum([len(samples[station_id]) for station_id in samples])
        progress_counter = 0
        for station_id in samples:
            for sample in samples[station_id]:
                if pd.isnull(sample['TD']) and pd.isnull(sample['TDmin']) and pd.isnull(sample['TDmax']) \
                        and pd.isnull(sample['TG']) and pd.isnull(sample['WSmax']) and pd.isnull(sample['WDmax'])\
                        and pd.isnull(sample['WS']) and pd.isnull(sample['WD']) and pd.isnull(sample['STDwd'])\
                        and pd.isnull(sample['Grad']) and pd.isnull(sample['NIP']) and pd.isnull(sample['DiffR'])\
                        and pd.isnull(sample['RH']) and pd.isnull(sample['Rain']):
                    _ = sample['stations'].pop(0)
                    if sample['stations']:
                        empty_samples.append(sample)
                progress_counter += 1
                progress = (progress_counter / length) * 100
                progress_var.set(progress)
                percentage_label.config(text=(('%.2f ' % progress) + '%'))
        if not empty_samples:
            break
        samples = empty_samples
    df.to_csv(f"./kitDataMerger/meteorology/meta_data_final.csv", index=False, encoding="utf-16")
    logging.info(f"The file was saved in the same directory of the original file as \"meta_data_final.csv\"")
    status_label.config(text="")

    return True