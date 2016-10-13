# Meetup Data Scrape for European Cities

A repo for scraping the Meetup api to get the total number of meetups for a list of cities.

Uses Google's geocoding API to get geo data for each city in the `data/raw/cities_list.txt` file. Currently only tested against European cities. Later scripts rely on the `geocoded_date_time.json` file for filtering events based on the bounding boxes of the relevant city.

Crawls the meetup api for all the meetup tech groups in those cities using Meetup's `smart_radius` feature and the city's latitude and longitude from the gecoding query.

Uses the group IDs to crawl for events data, then filter these for:
  - Events that have a venue
  - Events that are within the bounding box of the relevant city

The total number of events for each city is stored in `data/processed/events_in_cities_date_time.csv`.
