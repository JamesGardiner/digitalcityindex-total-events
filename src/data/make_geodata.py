# -*- coding: utf-8 -*-

"""Run this file to go from a list of cities to a list of
GeoJson data for each city, using the Google Geocoder."""

import codecs
import geocoder
import json
import os

from time import strftime


def main():
    # Project root
    project_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.pardir)

    # Path to the data file
    data_file = os.path.join(project_dir, 'data/raw/cities_list.txt')

    # Output file
    output_file = os.path.join(
        project_dir,
        'data/raw/geocoded_{}.json'.format(strftime("%Y%m%d_%H%M%S"))
    )

    # Use codecs to read the file, which contains unicode characters
    # using UTF-8 encoding
    file_object = codecs.open(data_file, 'r', encoding="UTF-8")

    # Strip the newlines, creating a list of cities
    data = [line.rstrip('\n') for line in file_object.readlines()]

    # Append ', europe' to each city name to limit the
    # Geocoding results
    data = [city + ', europe' for city in data]

    # Use geocoder's google implementation
    # to geocode the list of city names
    geocoded_data = [geocoder.google(city).geojson for city in data]

    # Save the results
    with open(output_file, 'w') as fp:
        json.dump(geocoded_data, fp)


if __name__ == "__main__":
    main()
