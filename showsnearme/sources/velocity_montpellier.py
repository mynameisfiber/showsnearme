from .ics_source import ICSSource
from .source import Source

URL = (
    "http://www.velocite-montpellier.fr/?"
    "plugin=all-in-one-event-calendar&"
    "controller=ai1ec_exporter_controller&"
    "action=export_events&"
    "no_html=true"
)


class VelocityMontpellier(Source, ICSSource):
    location = (43.6084009, 3.8793055)
    distance = 500

    def __init__(self, *args, **kwargs):
        super().__init__(url=URL, default_latlong=self.location,
                         default_venue="Montpellier")
