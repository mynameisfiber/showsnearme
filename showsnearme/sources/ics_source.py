import requests
from ics import Calendar

from .source import Source


class ICSSource:
    def __init__(self, url, *args, default_latlong=None, default_venue=None, **kwargs):
        self.default_venue = default_venue
        self.default_latlong = default_latlong or []
        self.url = url
        super().__init__(*args, **kwargs)

    def _load_calendar(self):
        return Calendar(requests.get(self.url).content.decode("utf8"))

    def __call__(self, *args, **kwargs):
        calendar = self._load_calendar()
        for event in calendar.events:
            venue = {
                "name": event.location or self.default_venue,
                "latitude": getattr(event.geo, "latitude", self.default_latlong[0]),
                "longitude": getattr(event.geo, "longitude", self.default_latlong[1]),
            }
            data = {
                "title": event.name,
                "venue": venue,
                "starts_at": event.begin.datetime,
                "ends_at": event.end.datetime,
                "url": event.url,
            }
            yield data
