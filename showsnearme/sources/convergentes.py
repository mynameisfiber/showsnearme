import logging
import re

import chompjs
import pytz
import dateparser
import requests

from .source import Source


logger = logging.getLogger(__name__)
URL = "https://www.convergent.es/?Agenda"


class ConvergentEs(Source):
    location = (43.6084009, 3.8793055)
    distance = 500
    tz = pytz.timezone("Europe/Paris")

    def __call__(self, *args, min_date=None, max_date=None, **kwargs):
        body = requests.get(URL).text
        all_events_match = re.search(
            r"var allEvents = \s?(?P<events>\[.*?]);", body, re.MULTILINE | re.DOTALL
        )
        if not all_events_match:
            return
        all_events = chompjs.parse_js_object(all_events_match.group("events"))
        for event in all_events:
            attributes = dict(
                re.findall(
                    r'data-(?P<key>[^=]+)=\"(?P<value>[^"]+)"', event["htmlattributes"]
                )
            )
            description = ", ".join(
                value
                for key, value in attributes.items()
                if key.startswith("checkboxListe")
            )
            yield {
                "title": event["title"],
                "description": description,
                "url": event["url"],
                "starts_at": dateparser.parse(event["start"]).replace(tzinfo=self.tz),
                "ends_at": dateparser.parse(event["end"]).replace(tzinfo=self.tz),
                "venue": {"name": "convergent·es"},
            }
