from .ics_source import ICSSource
from .source import Source

URL = "https://herault.demosphere.net/events.ics"


class DemosphereNet(Source, ICSSource):
    location = (43.6084009, 3.8793055)
    distance = 1000

    def __init__(self, *args, **kwargs):
        super().__init__(
            url=URL, default_latlong=self.location, default_venue="Montpellier"
        )
