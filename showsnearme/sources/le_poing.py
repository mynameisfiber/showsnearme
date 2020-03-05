from .source import Source
from urllib.parse import urljoin
import requests
from lxml import html
import json
import dateutil.parser
from ..geo import get_location


URL = "https://lepoing.net/evenements/"
MONTPELLIER_LATLON = (43.6084009, 3.8793055)


class LePoing(Source):
    location = MONTPELLIER_LATLON
    distance = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_events(self, dom):
        try:
            data_raw = dom.xpath('.//script[@type="application/ld+json"]')[0].text
        except IndexError:
            return []
        return json.loads(data_raw)

    def _get_next_page(self, dom):
        try:
            dom_a = dom.xpath('.//li[@class="tribe-events-nav-previous"]/a')[0]
            return urljoin(URL, dom_a.attrib['href'])
        except (IndexError, KeyError):
            return None

    def __call__(self, *args, min_date=None, max_date=None, **kwargs):
        data_url = URL
        while data_url:
            body = requests.get(data_url).content.decode('utf8')
            dom = html.fromstring(body)
            events = self._get_events(dom)
            data_url = self._get_next_page(dom)
            for event in events:
                try:
                    address = ", ".join(event['location']['address'][f]
                                        for f in ('streetAddress', 'addressLocality', 'postalCode'))
                    venue = {
                        "name": event['location']['name'],
                        **dict(zip(("latitude", "longitude"),
                                   get_location(address) or MONTPELLIER_LATLON))
                    }
                except KeyError:
                    venue = {
                        "name": "Montpellier",
                        "latitude": MONTPELLIER_LATLON[0],
                        "longitude": MONTPELLIER_LATLON[1],
                    }
                start_date = dateutil.parser.parse(event['startDate'])
                end_date = dateutil.parser.parse(event['endDate'])
                yield {
                    "title": event['name'],
                    "url": event['url'],
                    'starts_at': start_date,
                    'ends_at': end_date,
                    'venue': venue,
                }
            if min_date is not None and start_date < min_date:
                break
