# -*- coding: utf-8 -*-

"""Run this file to get group event data from the
groups downloaded by running make meetup_data"""
import dotenv
import json
import os

from .get_data import Meetup
from datetime import datetime
from operator import itemgetter
from time import strftime


def expand_meetup_group(alt_api, mu_data, group, events_from, events_to):
    """
    Expand the group JSON with list of events.

    Events:
    JSON for each event (in period events_from to events_to) stored in:
        group['events_in_window']
    """
    time = "%d,%d" % (datetime_to_epoch_ms(dt_frm), datetime_to_epoch_ms(dt_to))
    events = alt_api.events(group_id=group_id, status=status, time=time)
    gid = group['id']
    events = get_events(gid, events_from, events_to)
    group['events_in_window'] = events


def main():
    project_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.pardir)

    # Data dir
    data_path = os.path.join(project_dir, 'data/interim/')
    # load env vars
    dotenv_path = os.path.join(project_dir, '.env')
    dotenv.load_dotenv(dotenv_path)

    # Meetup API Key
    key = os.environ.get("API_KEY")

    # List of filenames
    data_files = os.listdir(data_path)

    # Check that there are actually files present
    if len(data_files) == 1 or len(data_files) < 1:
        msg = ("No files in the data directory." +
               " Please make sure you have run `make meetup_data` from" +
               " the project root directory first.")
        raise ValueError(msg)

    timestamps = []
    for file in data_files:
        if file == "__init__.py" or file == "cities_list.txt":
            pass
        else:
            name = file.strip('.json').split('_')
            timestamps.append((int(name[-2]), int(name[-1])))

    # Newest date
    max_date = (max(timestamps, key=itemgetter(0))[0])

    # Newest time
    max_time = (max(timestamps, key=itemgetter(0))[1])

    # Newest file name
    newest_file = "meetups_in_cities_{}_{}.json".format(max_date, max_time)

    with open(
        os.path.join(
            data_path,
            newest_file
        ), 'r'
    ) as fp:
        data = json.load(fp)

    events_from = datetime(2012, 1, 1)
    events_to = datetime.now()

    # Meetup object
    meetup = Meetup(key)
    result = {}
    for city in data:
        print('Getting events for {}.'.format(city))
        result[city] = []
        print('Groups:\t{}'.format(len(data[city])))
        for group in data[city]:
            gid = group["urlname"]
            print(gid)
            result[city].append(meetup.events(gid,
                                                   offset=0,
                                                   status='past',
                                                   page=200,))

    now = strftime('%Y%m%d_%H%M%S')
    out_file = 'data/interim/events_in_cities_{}.json'.format(now)
    out_file = os.path.join(project_dir, out_file)
    with open(out_file, 'w') as fp:
        json.dump(result, fp)

if __name__ == "__main__":
    main()
