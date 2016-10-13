# -*- coding: utf-8 -*-

"""Run this file to process the meetup data in
/data/interim/meetups_in_cities_*.json"""

import csv
import glob
import json
import os

from collections import namedtuple
from datetime import datetime
from operator import attrgetter
from operator import itemgetter


def check_files_exist(dir_path, globstring=None):
    files = glob.glob(os.path.join(dir_path, globstring))
    if len(files) < 1:
        msg = ("No files in {}.\n".format(dir_path) +
               " Please make sure you have run `make` from" +
               " the project root directory first.")
        raise ValueError(msg)
    else:
        return files


def get_timestamps(files):
    timestamps = []
    for file in files:
        if file == "__init__.py":
            pass
        else:
            name = file.strip('.json').split('_')
            timestamps.append((int(name[-2]), int(name[-1])))

    # Newest date
    max_date = (max(timestamps, key=itemgetter(0))[0])

    # Newest time
    max_time = (max(timestamps, key=itemgetter(0))[1])

    return (max_date, max_time)


def main():
    """The main process run when the file is called
    from the command line"""
    # Project root
    project_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.pardir)

    # Path to raw data directory
    raw_data_dir = os.path.join(project_dir, 'data/raw')

    # Path to the data directory
    data_dir = os.path.join(project_dir, 'data/interim/')

    # Wherethe new data gets saved
    out_dir = os.path.join(project_dir, 'data/processed/')

    # List of data filenames
    data_files = check_files_exist(data_dir,
                                   globstring='events*')

    max_date, max_time = get_timestamps(data_files)

    # Newest file name
    newest_file = "events_in_cities_{}_{}.json".format(max_date, max_time)

    # Out file
    out_file = "events_in_cities_{}_{}.csv".format(max_date, max_time)

    # Geocoded city data files
    cities_files = check_files_exist(project_dir,
                                     globstring='data/raw/geocoded*')

    # Load the data
    with open(os.path.join(data_dir, newest_file),
              mode='r',
              encoding='UTF-8') as fp:
        data = json.load(fp)

    # Newest timestamp from cities file
    max_date, max_time = get_timestamps(cities_files)

    # Filestring
    cities_file = 'geocoded_{}_{}.json'.format(max_date, max_time)

    # And path to file
    cities_path = os.path.join(raw_data_dir, cities_file)

    # load the list of cities selecting newest one
    with open(cities_path, 'r', encoding='utf-8') as fp:
        cities_list = json.load(fp)

    # Luxembourg can cause issues
    # check if there's no luxembourg, if not assume
    # that there is a null key, replace the key with luxembourg
    # will raise an exception if there is no luxembourg and no null
    if data.get('Luxembourg', True):
        data['Luxembourg'] = data.pop('null')

    # Named Tuple class to hold data
    # makes writing to csv easy later
    Data = namedtuple('Data', ['city', 'events'])
    tuples = []
    for city in data:
        tot_meetups = 0
        for place in cities_list:
            # Get the bbox of the current city
            if place.get('properties', {}).get('city') == city:
                bbox = place.get('properties', {}).get('bbox')
        for meetup in data[city]:
            for event in meetup:
                # Only events with venue data have lat lon
                if event.get('venue', False):
                    lon = event.get('venue').get('lon')
                    lat = event.get('venue').get('lat')
                    # Check event was inside city's bbox
                    if lon > bbox[0] and lon < bbox[2] and lat > bbox[2] and lat < bbox[3]:
                        if datetime.fromtimestamp(int(event.get('created') / 1000)).strftime("%Y-%M-%D") > "2015-09-31":
                            tot_meetups += 1
        print('{}:\t{}'.format(city, tot_meetups))
        tuples.append(Data(city, tot_meetups))

    # Using the filename from above so that timestamps match.
    # Can follow the trail of data...
    with open(os.path.join(out_dir, out_file), 'w', encoding='UTF-8') as out_fp:
        csv_out = csv.writer(out_fp)
        csv_out.writerow(['city', 'total'])
        csv_out.writerows([(name, data) for name, data in sorted(tuples, key=attrgetter('events'))])

if __name__ == "__main__":
    main()
