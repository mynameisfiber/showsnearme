import itertools
import textwrap

from colorama import Fore, Style
from colorama.ansi import OSC

WRAP_CHAR = "…"


def timedelta_str(dt):
    h = dt.seconds // 3600
    return f"{dt.days}d{int(h)}h"


def term_link(url, text):
    return f"{OSC}8;;{url}\a{text}{OSC}8;;\a"


def shorten_venue_name(name, length=24):
    name = name.split(",")[0].strip()
    if len(name) > length:
        name = name[:length] + WRAP_CHAR
    return name.replace(" ", "_")


def format_show(show, use_terminal_links=False, show_url=True, show_eta=False):
    if show_eta:
        timedisplay = timedelta_str(show["starts_at_timedelta"])
    else:
        timedisplay = show["starts_at"].strftime("%Hh%M")
    RA = Style.RESET_ALL
    title = textwrap.shorten(show["title"], width=64, placeholder=WRAP_CHAR)
    venue_name = shorten_venue_name(show["venue"]["name"])
    if use_terminal_links:
        title = term_link(show["url"], title)
        venue_name = term_link(
            f'https://www.google.com/maps/search/{show["venue"]["address"]}', venue_name
        )
    return "".join(
        (
            f"{Fore.BLUE}[{timedisplay}]{RA}",
            f'{Fore.GREEN}[{show["distance"]:04.1f}{show["distance_units"]}]{RA}',
            f" {title}",
            f" {Fore.RED}@{venue_name}{RA}",
            (f' {show["url"]}' if show_url else ""),
        )
    )


def print_shows(
    shows,
    chunk_days=False,
    n_shows_daily=None,
    show_url=True,
    show_eta=False,
    use_terminal_links=False,
    **kwargs,
):
    print_params = {"show_eta": show_eta, "use_terminal_links": use_terminal_links}
    if not chunk_days:
        for show in shows:
            print(format_show(show, show_url=show_url, **print_params))
    else:
        shows_groups = itertools.groupby(shows, lambda show: show["num_days"])
        future_strings = {
            -1: "Yesterday",
            0: "Today",
            1: "Tomorrow",
            2: "Day after tomorrow",
        }
        first_iter = True
        for day, day_shows in shows_groups:
            if not first_iter:
                print()
            day_str = future_strings.get(day, f"In {day} days")
            print(f"{Style.BRIGHT}{day_str}{Style.RESET_ALL}")
            for i, show in enumerate(day_shows):
                if n_shows_daily and i >= n_shows_daily:
                    print(f"\t{Fore.RED}...more shows cut...{Style.RESET_ALL}")
                    break
                display = format_show(show, show_url=show_url, **print_params)
                print(f"\t{display}")
            first_iter = False
