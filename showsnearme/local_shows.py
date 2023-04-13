import datetime
import itertools
import logging
from collections import ChainMap

import pytz
from slugify import slugify

from . import geo
from .sources import Sources

logger = logging.getLogger(__name__)


def iter_skip_execption(iter_):
    try:
        yield from iter_
    except Exception as e:
        logger.debug(f"Exception: {e})", exc_info=True)


def query_shows(
    location=None,
    n_shows=5,
    n_start_days=None,
    n_end_days=None,
    chunk_days=False,
    passed_shows=True,
    imperial=False,
    max_distance=None,
    debug=False,
    **kwargs,
):
    now = datetime.datetime.now(pytz.utc)
    if n_start_days is not None:
        min_date = (now - datetime.timedelta(days=n_start_days)).replace(
            hour=0, minute=0, second=0
        )
    else:
        min_date = None

    if n_end_days is not None:
        max_date = (now + datetime.timedelta(days=n_end_days)).replace(
            hour=23, minute=59, second=59
        )
    else:
        max_date = None

    location = location or geo.get_current_location()
    shows = []
    sources = Sources(location, max_distance)
    for source_ins, source in sources(min_date=min_date, max_date=max_date):
        source_shows = []
        for show in iter_skip_execption(source):
            logger.debug(f"Considering show: {show}")
            if len(source_shows) == n_shows:
                logger.debug(f"Reached max number of shows: {n_shows}")
                break
            if all(f in show["venue"] for f in ("latitude", "longitude")):
                venue_location = [
                    float(show["venue"]["latitude"]),
                    float(show["venue"]["longitude"]),
                ]
            else:
                venue_location = source_ins.location
            distance = show["distance"] = geo.haversine(
                location, venue_location, imperial=imperial
            )
            show["distance_units"] = "km" if not imperial else "mi"
            if max_distance and distance > max_distance:
                logger.debug(f"Show is too far away: {distance} > {max_distance}")
                continue

            starts_at = show["starts_at"]
            ends_at = show.get("ends_at")
            now = datetime.datetime.now(starts_at.tzinfo)
            if not passed_shows and starts_at < now:
                logger.debug(f"Show is in the past: {starts_at} < {now}")
                continue

            show["starts_at_timedelta"] = starts_at - now
            show["num_days"] = (starts_at.date() - now.date()).days
            if min_date and ends_at and ends_at < min_date:
                logger.debug(f"Show is not within timerange: {ends_at} < {min_date}")
                continue
            elif max_date and starts_at > max_date:
                logger.debug(f"Show is too far in the future: {starts_at} > {max_date}")
                break
            logger.debug("Adding show to list")
            show["source"] = source_ins
            source_shows.append(show)
        shows.extend(source_shows)
    shows.sort(key=lambda item: (item["starts_at"], item["title"]))
    shows = dedup_shows(shows)
    return shows


def merge_shows(shows):
    shows = sorted(shows, key=lambda s: getattr(s["source"], "priority", 0))
    logger.debug(f"merging: {shows}")
    return dict(ChainMap(*shows))


def dedup_shows(shows):
    _iter = itertools.groupby(shows, lambda s: slugify(s["title"]))
    return [merge_shows(show_group) for _, show_group in _iter]
