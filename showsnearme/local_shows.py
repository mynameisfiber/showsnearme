import requests
import geocoder
import dateutil.parser

from math import radians, cos, sin, asin, sqrt
from operator import itemgetter
import datetime


_CITY_TO_REGION = {
    'new york': 1,
    'los angeles': 3,
    'chicago': 2
}
CITIES = list(_CITY_TO_REGION.keys())
URL = ("https://www.ohmyrockness.com/api/shows.json?"
       "index=true&page={page}&per=50&regioned={region}")


def generate_shows(city='new york', token=None):
    page = 1
    seen_ids = set()

    def is_new(show):
        _id = show['id']
        not_in = _id not in seen_ids
        seen_ids.add(_id)
        return not_in
    queue = []
    while True:
        req = requests.get(
            URL.format(region=_CITY_TO_REGION[city], page=page),
            headers={'authorization': 'Token token="' + token}
        )
        if req.status_code == 401:
            raise Exception("Expired/Invalid authorization token")
        data = req.json()
        for show in data:
            show['starts_at'] = dateutil.parser.parse(show['starts_at'])
        queue.extend(filter(is_new, data))
        if len(queue) >= 100:
            #  the responses from ohmyrockness are not exactly in chronological
            #  order. as a result, we fetch 100 at a time, sort them, then only
            #  use the first 50, and fetch more. This hopefully gives us enough
            #  of a pool to smooth things out so _this generator_ yields shows
            #  in chronological order
            queue.sort(key=itemgetter('starts_at'))
            yield from queue[:50]
            queue = queue[50:]
        page += 1


def get_location(location=None):
    if location is None:
        location = geocoder.ip('me')
    else:
        location = geocoder.google(location)
    return location.latlng


def haversine(A, B, imperial=False):
    """
    Calculate the great circle distance between two points on the earth
    (specified in decimal degrees)
    From:
        https://stackoverflow.com/a/4913653
    """
    (lat1, lon1) = A
    (lat2, lon2) = B

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in km
    if imperial:
        r = 3956  # Radius of earth in miles
    return c * r


def query_shows(location=None, n_shows=5, n_start_days=None, n_end_days=None,
                chunk_days=False, passed_shows=True, imperial=False, city=None,
                token=None, **kwargs):
    location = location or get_location()
    shows = []
    for show in generate_shows(city=city, token=token):
        if len(shows) == n_shows:
            break
        venue_location = [float(show['venue'].get(f) or 0.0)
                          for f in ('latitude', 'longitude')]
        show['distance'] = haversine(location, venue_location,
                                     imperial=imperial)
        show['distance_units'] = 'km' if not imperial else 'mi'

        starts_at = show['starts_at']
        now = datetime.datetime.now(starts_at.tzinfo)
        if starts_at < now:
            continue

        show['starts_at_timedelta'] = (starts_at - now)
        show['num_days'] = num_days = (starts_at.date() - now.date()).days
        if n_start_days and num_days < n_start_days:
            continue
        elif n_end_days and num_days >= n_end_days:
            break
        shows.append(show)
    shows.sort(key=lambda item: (chunk_days and item['num_days'] or 0,
                                 item['distance']))
    return shows
