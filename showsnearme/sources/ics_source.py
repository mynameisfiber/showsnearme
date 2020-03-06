import requests
from ics import Calendar

from ..geo import clean_address, get_location
from .source import Source


class ICSSource:
    location = (0, 0)

    def __init__(self, url, *args, default_latlong=None, default_venue=None, **kwargs):
        self.default_venue = default_venue
        self.default_latlong = default_latlong or []
        self.url = url
        super().__init__(*args, **kwargs)

    def _load_events(self, min_date, max_date):
        cal = Calendar(requests.get(self.url).content.decode("utf8"))
        events = sorted(cal.events, key=lambda e: e.begin.datetime)
        if min_date or max_date:
            events = filter(
                lambda e: (
                    (min_date and e.end.datetime >= min_date)
                    or (max_date and e.begin.datetime <= max_date)
                ),
                events,
            )
        return events

    def _get_location(self, event):
        latlon = None
        if getattr(event.geo, "latitude", None) and getattr(
            event.geo, "longitude", None
        ):
            latlon = (event.geo.latitude, event.geo.longitude)
        elif getattr(event, "location", None):

            latlon = get_location(event.location)
        if not latlon:
            latlon = self.location
        return latlon

    def __call__(self, *args, min_date=None, max_date=None, **kwargs):
        events = self._load_events(min_date, max_date)
        for event in events:
            if event.location:
                event.location = clean_address(event.location)
            latlon = self._get_location(event)
            venue = {
                "name": event.location or self.default_venue,
                "address": event.location,
                "latitude": latlon[0],
                "longitude": latlon[1],
            }
            data = {
                "title": event.name,
                "venue": venue,
                "starts_at": event.begin.datetime,
                "ends_at": event.end.datetime,
                "url": event.url,
            }
            yield data
