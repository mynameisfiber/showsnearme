from itertools import zip_longest
from .. import geo


class Sources:
    __registry = []

    def __init__(self, location, distance, *args, **kwargs):
        self.instances = [i(*args, **kwargs) for i in self.__registry
                          if geo.haversine(location, i.location) <= distance + i.distance]

    @classmethod
    def register(self, cls):
        self.__registry.append(cls)

    def __call__(self):
        iters = [i() for i in self.instances]
        for values in zip_longest(*iters):
            yield from filter(None, values)
