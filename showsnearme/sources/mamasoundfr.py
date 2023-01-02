from datetime import timedelta, datetime
import json
import logging
import re

import dateparser
import pytz
import requests
from lxml import etree

from .source import Source


logger = logging.getLogger(__name__)
URL = "http://api.mamasound.fr/Event"
REMOVE_TAGS = re.compile(r"<[^>]+>")


class MamaSoundFR(Source):
    location = (43.604611, 3.8783639)
    distance = 100
    timezone = pytz.timezone("europe/paris")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.one_hour = timedelta(hours=1)

    def _create_query(self, start_time: datetime | None = None):
        start_time = start_time or datetime.now()
        timestamp = int(start_time.timestamp() * 1000)
        query = {"$query":{"$or":[{"_cls":"Concert","schedule":{"$elemMatch":{"startTM":{"$gt":timestamp}}}},{"_cls":"Concert","startTM":{"$gt":timestamp}},{"_cls":"Theatre","schedule":{"$elemMatch":{"startTM":{"$gt":timestamp}}}},{"_cls":"Expo","haveVerni":True,"verniTM":{"$gt":timestamp}}]},"$limit":200,"$orderby":{"startTM":1}}
        return query

    def _clean_data(self, data):
        results = data["result"]['items']
        refs = data["refs"]
        for result in results:
            update = {}
            for key, value in result.items():
                if isinstance(value, dict) and 'objId' in value:
                    if ref_data := refs.get(value["objId"]):
                        update[key] = ref_data
            result.update(update)
        return results

    def _parse_venue(self, place):
        longlat = place['address']['geoPoint']
        if "address" in place["address"]:
            address = place["address"]["address"]
        elif "description" in place:
            address = REMOVE_TAGS.sub("", place["description"]).strip()
        else:
            address = None
        return {
            "name": place['label'],
            "address": address,
            "longitude": longlat[0],
            "latitude": longlat[1],
        }

    def __call__(self, *args, min_date: datetime | None =None, max_date: datetime | None=None, **kwargs):
        query = self._create_query(start_time=min_date)
        data = requests.get(URL, params={"q": json.dumps(query)}).json()
        print("!!!!!!!!!!!!!!!!!!!!!!!!")
        for event in self._clean_data(data):
            starts_at = datetime.fromtimestamp(event['startTM'] / 1000.0, tz=self.timezone)
            if min_date and starts_at < min_date:
                continue
            elif max_date and starts_at + self.one_hour > max_date:
                break

            title = event['title']
            url = f"http://www.mamasound.fr/{event['_cls']}/{event['_alias']}"
            venue = self._parse_venue(event["place"])
            data = {
                "title": title,
                "url": url,
                "starts_at": starts_at,
                "ends_at": starts_at + self.one_hour,
                "venue": venue,
            }
            logger.debug(f"Mamasound: {data}")
            yield data

