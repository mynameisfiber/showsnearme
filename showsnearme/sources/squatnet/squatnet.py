import logging
from urllib.parse import urljoin

import dateparser
import requests
from lxml import html

from showsnearme.geo import get_location

logger = logging.getLogger(__name__)
base_url = "https://radar.squat.net/en/events/"


class SquatNet:
    priority = 100
    location = (0, 0)

    def __init__(self, city=None, country=None):
        self.city = city
        self.country = country

    @property
    def url(self):
        url = base_url
        if self.country:
            url = urljoin(url, f"country/{self.country}")
        if self.city:
            url = urljoin(url, f"city/{self.city}")
        return url

    def _get_next_page(self, dom):
        try:
            item = dom.xpath(".//li[contains(@class, 'pager-next')]/a")[0]
            return item.attrib["href"]
        except (IndexError, KeyError):
            return None

    def _get_events(self, dom):
        return dom.xpath('.//article[@typeof="Event"]')

    def _parse_venue(self, event):
        location = event.find('.//div[@property="location"]')
        address = ", ".join(
            l.strip() for l in location.find('.//*[@typeof="PostalAddress"]').itertext()
        )
        try:
            name = location.find('.//*[@property="name"]').text
        except AttributeError:
            try:
                name = event.find('.//*[@class="group"]//*[@property="schema:name"]').text
            except AttributeError:
                name = address
        try:
            return {
                "name": name,
                "address": address,
                **dict(
                    zip(
                        ("latitude", "longitude"),
                        get_location(address) or self.location,
                    )
                ),
            }
        except KeyError:
            pass
        return {
            "name": name or self.city,
            "address": address,
            "latitude": self.location[0],
            "longitude": self.location[1],
        }

    def __call__(self, *args, **kwargs):
        data_url = self.url
        while data_url:
            try:
                body = requests.get(data_url, timeout=5).content.decode("utf8")
            except ConnectionError:
                return
            dom = html.fromstring(body)
            events = self._get_events(dom)
            if not events:
                break
            data_url = self._get_next_page(dom)
            for event in events:
                link_dom = event.find('.//h4[@property="schema:name"]/a')
                start_date = event.find('.//span[@property="schema:startDate"]').attrib[
                    "content"
                ]
                end_date = event.find('.//span[@property="schema:endDate"]').attrib[
                    "content"
                ]
                yield {
                    "title": link_dom.text,
                    "url": link_dom.attrib["href"],
                    "starts_at": dateparser.parse(start_date),
                    "ends_at": dateparser.parse(end_date),
                    "venue": self._parse_venue(event),
                }
