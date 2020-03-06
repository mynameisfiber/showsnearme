import json
from urllib.parse import urljoin

import dateutil.parser
import requests
from lxml import html

from ..geo import get_location
from .source import Source

URL = "https://lepoing.net/evenements/"


class LePoing(Source):
    location = (43.6084009, 3.8793055)
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
            return urljoin(URL, dom_a.attrib["href"])
        except (IndexError, KeyError):
            return None

    def __call__(self, *args, min_date=None, max_date=None, **kwargs):
        data_url = URL
        while data_url:
            body = requests.get(data_url).content.decode("utf8")
            dom = html.fromstring(body)
            events = self._get_events(dom)
            data_url = self._get_next_page(dom)
            for event in events:
                start_date = dateutil.parser.parse(event["startDate"])
                end_date = dateutil.parser.parse(event["endDate"])
                if (min_date and start_date < min_date) or (
                    max_date and end_date > max_date
                ):
                    continue
                try:
                    address = ", ".join(
                        event["location"]["address"][f]
                        for f in ("streetAddress", "addressLocality", "postalCode")
                        if event["location"].get(f)
                    )
                    venue = {
                        "name": event["location"]["name"],
                        "address": address,
                        **dict(
                            zip(
                                ("latitude", "longitude"),
                                get_location(address) or self.location,
                            )
                        ),
                    }
                except KeyError:
                    venue = {
                        "name": "Montpellier",
                        "address": "Montpellier",
                        "latitude": self.location[0],
                        "longitude": self.location[1],
                    }
                yield {
                    "title": event["name"],
                    "url": event["url"],
                    "starts_at": start_date,
                    "ends_at": end_date,
                    "venue": venue,
                }
            if min_date is not None and start_date < min_date:
                break
