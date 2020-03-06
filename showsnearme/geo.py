import re
from functools import lru_cache
from math import asin, cos, radians, sin, sqrt

import geocoder


def clean_address(address):
    address = address.replace("\n", ", ")
    address = _address_not_overlap(address)
    return address


def _address_not_overlap(address):
    address_parts_clean = []
    address_lower = address.lower()
    address_parts = address.split(",")
    i = 0
    for a in address_parts:
        i += len(a) + 1
        if a and a.lower() not in address_lower[i:]:
            address_parts_clean.append(a.strip())
    return ", ".join(address_parts_clean)


def get_current_location():
    return geocoder.ip("me").latlng


@lru_cache(maxsize=None)
def get_location(address):
    if not address:
        return None
    location = geocoder.osm(address)
    try:
        if location.ok:
            return [location.osm["y"], location.osm["x"]]
    except KeyError:
        pass
    try:
        index = address.index(",")
    except ValueError:
        return None
    return get_location(address[index + 1 :].strip())


def haversine(A, B, imperial=False):
    """
    Calculate the great circle distance between two points on the earth
    (specified in decimal degrees)
    From:
        https://stackoverflow.com/a/4913653
    """
    (lat1, lon1) = A
    (lat2, lon2) = B

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in km
    if imperial:
        r = 3956  # Radius of earth in miles
    return c * r
