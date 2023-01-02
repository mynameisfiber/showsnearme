from datetime import timedelta, time, datetime
import logging
import re

import dateparser
import pytz
import requests
from lxml import etree, html

from .source import Source


logger = logging.getLogger(__name__)
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
        self.zero_time = time(0, 0)
        self.one_hour = timedelta(hours=1)

    def _parsedate(self, text) -> datetime | None:
        if "EN SOIRÉE" in text.upper():
            return datetime(1, 1, 1, hour=22)
        elif match := re.match('([0-9]{1,2})H', text):
            hour = int(match.groups()[0])
            return datetime(1, 1, 1, hour=hour)
        else:
            return dateparser.parse(text)

    def __call__(self, *args, min_date=None, max_date=None, **kwargs):
        data = requests.get(URL).content
        dom = etree.fromstring(data)
        event_blocks = dom.findall(".//item")
        ns = {'content':'http://purl.org/rss/1.0/modules/content/'}
        events = []
        for block in event_blocks:
            blocktitle = block.find('./title').text
            if not "AGENDA" in blocktitle:
                continue
            blockdate = self._parsedate(block.find('./pubDate').text)
            if blockdate:
                blockyear = blockdate.year
            else:
                blockyear = datetime.now().year
            url = block.find('./link').text
            content = block.find('./content:encoded', ns)
            blockdom = html.fromstring(content.text)
            curdate = None
            curtime = None
            for paragraph in blockdom.findall('./p'):
                ptext = "".join(paragraph.itertext()).strip()
                if not ptext:
                    continue
                date = self._parsedate(ptext)
                if date is not None:
                    if date.time() == self.zero_time:
                        curdate = date.replace(year=blockyear)
                    else:
                        curtime = date.time()
                elif curdate != None and curtime != None and '[ANNULÉ]' not in ptext:
                    starts_at = datetime.combine(curdate, curtime, tzinfo=self.timezone)
                    curtime = None
                    if min_date and starts_at < min_date:
                        continue
                    title = paragraph.find('.//strong').text.title()
                    events.append({
                        "title": title,
                        "url": url,
                        "starts_at": starts_at,
                        "ends_at": starts_at + self.one_hour,
                        "venue": self.venue,
                    })
        events.sort(key=lambda e: e['starts_at'])
        yield from events
