from .source import Source
from .ics_source import ICSSource


URL = ("http://www.velocite-montpellier.fr/?"
       "plugin=all-in-one-event-calendar&"
       "controller=ai1ec_exporter_controller&"
       "action=export_events&"
       "no_html=true")

MONTPELLIER_LATLON = (43.6084009, 3.8793055)


class VelocityMontpellier(Source, ICSSource):
    location = MONTPELLIER_LATLON
    distance = 500

    def __init__(self):
        super().__init__(url=URL, default_latlong=MONTPELLIER_LATLON)
