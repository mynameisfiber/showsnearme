import re

from .ics_source import ICSSource
from .source import Source

URL = "https://www.aleale.org/feed/ics?show_recurrent=true"


class AleAle(Source, ICSSource):
    location = (43.6084009, 3.8793055)
    distance = 1000
    priority = 100

    def __init__(self, *args, **kwargs):
        super().__init__(
            url=URL, default_latlong=self.location, default_venue="Montpellier"
        )

    def __call__(self, *args, **kwargs):
        clean_title = re.compile("\[[^]]+\]\s?")
        for event in super().__call__(*args, **kwargs):
            event["title"] = clean_title.sub("", event["title"])
            yield event
