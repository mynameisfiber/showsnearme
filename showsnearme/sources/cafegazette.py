from datetime import timedelta

import dateparser
import pytz
import requests
from lxml import etree

from .source import Source

URL = "https://www.gazettecafe.com/blog-feed.xml"


class CafeGazette(Source):
    location = (43.604611, 3.8783639)
    distance = 100
    timezone = pytz.timezone("europe/paris")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.venue = {
            "name": "Cafe Gazette",
            "address": "6 Rue Levat, 34000 Montpellier",
            "latitude": self.location[0],
            "longitude": self.location[1],
        }
        self.one_hour = timedelta(hours=1)

    def __call__(self, *args, min_date=None, max_date=None, **kwargs):
        data = requests.get(URL).content
        dom = etree.fromstring(data)
        for event in dom.findall(".//item"):
            try:
                title_raw = event.find(".//title").text
                date_str, time_str, title = map(str.strip, title_raw.split(" - ", 2))
            except ValueError:
                continue
            date = dateparser.parse(date_str)
            time = dateparser.parse(time_str)
            starts_at = date.replace(
                hour=time.hour, minute=time.minute, tzinfo=self.timezone
            )
            if starts_at < min_date:
                continue
            elif starts_at + self.one_hour > max_date:
                break
            title = title.title()
            url = event.find(".//link").text
            yield {
                "title": title,
                "url": url,
                "starts_at": starts_at,
                "ends_at": starts_at + self.one_hour,
                "venue": self.venue,
            }
