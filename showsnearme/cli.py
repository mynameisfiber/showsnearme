import argparse
from showsnearme import (local_shows, display, CITIES, hack)


parser = argparse.ArgumentParser(
    description='Find local shows',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('location', type=str, nargs='?',
                    help='location of search (default: geoip location)')
parser.add_argument('--city', type=str, default=CITIES[0], choices=CITIES,
                    help='Which ohmyrockness city to look up')
parser.add_argument('-N, --n-shows', type=int, dest='n_shows',
                    help='Number of total shows to show')
parser.add_argument('-n, --n-shows-daily', type=int, dest='n_shows_daily',
                    help='Number of shows per day maximum to show')

parser.add_argument('-A, --end-days', type=int,
                    dest='n_end_days',
                    help='Number of days from now to end query')
parser.add_argument('-B, --start-days', type=int, default=0,
                    dest='n_start_days',
                    help='Number of days from now to start query')

parser.add_argument('--token', type=str,
                    help='Authorization token for ohmyrockness')

parser.add_argument('--no-chunk-days', dest='chunk_days', action='store_false',
                    help="Don't chunk results into calendar days")
parser.add_argument('--show-old', dest='pased_shows', action='store_true',
                    help='Show shows that have already started')
parser.add_argument('--hide-url', dest='show_url', action='store_false',
                    help='Whether to hide URLs from output')
parser.add_argument('--show-eta', dest='show_eta', action='store_true',
                    help='Show ETA until show instead of absolute time')
parser.add_argument('--imperial', dest='imperial', action='store_true',
                    help='Show distances in miles instead of km')

parser.add_argument('--debug', action='store_true', help='Debug Output')


def main():
    args = parser.parse_args()

    args.location = local_shows.get_location(args.location)
    args.token = args.token or hack.get_authorization_token()
    if not (args.n_shows or args.n_end_days):
        args.n_shows = 5

    params = args.__dict__
    if args.debug:
        print(params)

    shows = local_shows.query_shows(**params)
    display.print_shows(
        shows,
        **params
    )


if __name__ == "__main__":
    main()
