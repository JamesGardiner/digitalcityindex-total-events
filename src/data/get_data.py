# -*- coding: utf-8 -*-

"""Run this file to get meetup data from the cities list
in project_directory/data/raw/cities.csv"""
import dotenv
import json
import os
import ratelim
import requests

from datetime import datetime
from time import strftime
from operator import itemgetter

# Set ratelimit at 9000 requests per hour
RATELIM_DUR = 60 * 60
RATELIM_QUERIES = 5000

DEFAULT_PAGINATION_COUNT = 200


class Meetup(object):
    def __init__(self, api_key):
        self._api_key = api_key
        self._base_url = 'https://api.meetup.com/'
        self._dt_start = datetime.now()

    @ratelim.patient(RATELIM_QUERIES, RATELIM_DUR)
    def query_gateway(self, url, params={}):
        """
        Run query with complete url `url`. The main gateway to Meetup API.

        Returns:
        JSON. Typical Meetup response is 'meta' and 'results'.
        In addition, this function adds a 'rate' sub-dictionary.

        rate.limit:              Absolute max number requests per window.
        rate.limit_remaining:    Remaining requests in current window.
        rate.reset:              Time (secs) until window is reset.

        More info at: http://www.meetup.com/meetup_api/#limits
        """
        # Do work
        return requests.get(url=url, params=params)

    def query_get(self, path, params={}):
        """
        Issue GET query to meetup API. Automatically adds API key.

        path: URL path. Not including leading slash.
        get_parmas: dict of GET parameters.
        """
        d = dict(params)
        if 'sig' not in d:
            d['key'] = self._api_key
        if 'format' not in d:
            d['format'] = 'json'
        if 'page' not in d:
            d['page'] = DEFAULT_PAGINATION_COUNT

        out = self.query_gateway(self._base_url + path, params=d)
        return out

    def query_get_all_results(self, path, params):
        """
        Obtain all results from an API query. Follows 'meta.next', concatenating
        multiple HTTP responses as needed.

        Returns: sequence of results.
        """
        results = []

        resp = self.query_get(path, params)
        while True:
            # Extend results
            results.extend(resp.json())

            # Prepare for next iteration
            next_url = resp.links.get('next', {}).get('url', None)
            if next_url is None:
                break
            params['offset'] += 1
            print('Offset:\t{}'.format(params['offset']))
            resp = self.query_get(path, params)
        return results

    def query_get_all_events(self, path, params):
        """
        Obtain all results from the API events query. Follows 'meta.prev',
        concatenating multiple HTTP responses as needed.

        Returns: sequence of results.
        """
        results = []

        resp = self.query_get(path, params)
        while True:
            # Extend results
            results.extend(resp.json())

            # Prepare for next iteration
            next_url = resp.links.get('prev', {}).get('url', None)
            if next_url is None:
                break
            params['offset'] += 1
            print('Offset:\t{}'.format(params['offset']))
            resp = self.query_get(path, params)
        return results

    def groups(self, **kwargs):
        """Returns list of results (groups)."""
        params = kwargs
        ret = self.query_get_all_results('find/groups', params)
        return ret

    def events(self, group_name, **kwargs):
        """Returns a list of events assosciated with a group."""
        params = kwargs
        ret = self.query_get_all_events('{}/events'.format(group_name), params)
        return ret


def main():
    # Project dir
    project_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                               os.pardir)

    # Data dir
    raw_data = os.path.join(project_dir, 'data/raw/')

    # load env vars
    dotenv_path = os.path.join(project_dir, '.env')
    dotenv.load_dotenv(dotenv_path)

    # List of filenames
    data_files = os.listdir(raw_data)

    # Check that there are actually files present
    if len(data_files) == 1 or len(data_files) < 1:
        msg = ("No files in the data directory." +
               " Please make sure you have run `make` from" +
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
    newest_file = "geocoded_{}_{}.json".format(max_date, max_time)

    with open(
        os.path.join(
            raw_data,
            newest_file
        ), 'r'
    ) as fp:
        geocoded_data = json.load(fp)

    # Meetup API Key
    key = os.environ.get("API_KEY")

    # Meetup object
    meetup = Meetup(key)
    result = {}
    for city in geocoded_data:
        country = city.get('properties', {}).get('country')
        lat = city.get('properties', {}).get('lat')
        lon = city.get('properties', {}).get('lng')
        city_name = city.get('properties', {}).get('city', None)
        print('Lat: {}\tLng: {}\tCity: {}\tCountry: {}'.format(lat, lon, city_name, country))
        out = meetup.groups(
            country=country,
            lat=lat,
            lon=lon,
            category=34,
            radius='smart',
            offset=0,
        )

        result[city_name] = out

    now = strftime('%Y%m%d_%H%M%S')
    out_file = 'data/interim/meetups_in_cities_{}.json'.format(now)
    out_file = os.path.join(project_dir, out_file)
    with open(out_file, 'w') as fp:
        json.dump(result, fp)


if __name__ == '__main__':
    main()
