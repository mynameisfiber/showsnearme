import geocoder
from math import radians, cos, sin, asin, sqrt


def get_location(location=None):
    if location is None:
        location = geocoder.ip('me')
    else:
        location = geocoder.google(location)
    return location.latlng


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
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in km
    if imperial:
        r = 3956  # Radius of earth in miles
    return c * r

