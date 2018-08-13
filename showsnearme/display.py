from colorama import (Fore, Style)
import itertools


def timedelta_str(dt):
    h = dt.seconds // 3600
    return f'{dt.days}d{int(h)}h'


def format_show(show, show_url=True):
    artists = [band['name'] for band in show['cached_bands']]
    if len(artists) > 3:
        artists = [*artists[:3], '...']
    RA = Style.RESET_ALL
    return "".join((
        f'{Fore.GREEN}[{show["distance"]:0.2f}{show["distance_units"]}]{RA}',
        f'{Fore.BLUE}[T-{timedelta_str(show["starts_at_timedelta"])}]{RA}',
        f' {", ".join(artists)}',
        f' {Fore.RED}@{show["venue"]["name"].replace(" ", "_")}{RA}',
        (f' ({show["url"]})' if show_url else ''),
    ))


def print_shows(shows, chunk_days=False, n_shows_daily=None,
                show_url=True, **kwargs):
    if not chunk_days:
        for show in shows:
            print(format_show(show, show_url=show_url))
    else:
        shows_groups = itertools.groupby(
            shows,
            lambda show: show['num_days']
        )
        future_strings = {
            0: 'Today',
            1: 'Tomorrow',
            2: 'Day after tomorrow'
        }
        first_iter = True
        for day, day_shows in shows_groups:
            if not first_iter:
                print()
            day_str = future_strings.get(day, f'In {day} days')
            print(f"{Style.BRIGHT}{day_str}{Style.RESET_ALL}")
            for i, show in enumerate(day_shows):
                if n_shows_daily and i >= n_shows_daily:
                    print(f"\t{Fore.RED}...more shows cut...{Style.RESET_ALL}")
                    break
                print(f"\t{format_show(show, show_url=show_url)}")
            first_iter = False
