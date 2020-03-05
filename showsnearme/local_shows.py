import datetime

from .sources import Sources
from . import geo


def query_shows(location=None, n_shows=5, n_start_days=None, n_end_days=None,
                chunk_days=False, passed_shows=True, imperial=False, max_distance=None,
                **kwargs):
    location = location or geo.get_location()
    shows = []
    sources = Sources(location, max_distance)
    for show in sources():
        if len(shows) == n_shows:
            break
        venue_location = [float(show['venue'].get(f) or 0.0)
                          for f in ('latitude', 'longitude')]
        show['distance'] = geo.haversine(location, venue_location,
                                         imperial=imperial)
        show['distance_units'] = 'km' if not imperial else 'mi'

        starts_at = show['starts_at']
        now = datetime.datetime.now(starts_at.tzinfo)
        if not passed_shows and starts_at < now:
            continue

        show['starts_at_timedelta'] = (starts_at - now)
        show['num_days'] = num_days = (starts_at.date() - now.date()).days
        if n_start_days and -1 * num_days < n_start_days:
            continue
        elif n_end_days and num_days >= n_end_days:
            break
        shows.append(show)
    shows.sort(key=lambda item: (chunk_days and item['num_days'] or 0,
                                 item['distance']))
    return shows
