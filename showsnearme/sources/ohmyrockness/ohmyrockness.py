import requests 
from .hack import get_authorization_token
from ..source import Source
import dateutil.parser
from operator import itemgetter


_CITY_TO_REGION = {
    'new york': 1,
    'los angeles': 3,
    'chicago': 2
}
CITIES = list(_CITY_TO_REGION.keys())
URL = ("https://www.ohmyrockness.com/api/shows.json?"
       "index=true&page={page}&per=50&regioned={region}")


class _OhMyRockness(Source):
    def __init__(self, city='new york', token=None):
        self.token = token or get_authorization_token()
        self.city = city
        self.name = f'OhMyRockness.{city.replace(" ","_")}'
        self.__seen_ids = set()
        super().__init__()

    def _is_new(self, show):
        _id = show['id']
        not_in = _id not in self.__seen_ids
        self.__seen_ids.add(_id)
        return not_in

    def __call__(self):
        page = 1
        seen_ids = set()
    
        queue = []
        while True:
            req = requests.get(
                URL.format(region=_CITY_TO_REGION[self.city], page=page),
                headers={'authorization': 'Token token="' + self.token}
            )
            if req.status_code == 401:
                raise Exception("Expired/Invalid authorization token")
            data = req.json()
            for show in data:
                show['starts_at'] = dateutil.parser.parse(show['starts_at'])
                artists = [band['name'] for band in show['cached_bands']]
                if len(artists) > 3:
                    artists = [*artists[:3], '...']
                show['title'] = ",".join(artists)
            queue.extend(filter(self._is_new, data))
            if len(queue) >= 100:
                #  the responses from ohmyrockness are not exactly in chronological
                #  order. as a result, we fetch 100 at a time, sort them, then only
                #  use the first 50, and fetch more. This hopefully gives us enough
                #  of a pool to smooth things out so _this generator_ yields shows
                #  in chronological order
                queue.sort(key=itemgetter('starts_at'))
                yield from queue[:50]
                queue = queue[50:]
            page += 1
    

class OhMyRocknessNewYork(_OhMyRockness):
    location = (40.7128, 74.0060)
    def __init__(self, *args, **kwargs):
        super().__init__(city='new york', *args, **kwargs)


class OhMyRocknessChicago(_OhMyRockness):
    location = (41.8781, 87.6298)
    def __init__(self, *args, **kwargs):
        super().__init__(city='chicago', *args, **kwargs)


class OhMyRocknessLosAngeles(_OhMyRockness):
    location = (34.0522, 118.2437)
    def __init__(self, *args, **kwargs):
        super().__init__(city='los angeles', *args, **kwargs)
