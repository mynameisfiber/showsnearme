import re
import html
import requests
from urllib.parse import urljoin


BASE_URL = 'https://www.ohmyrockness.com/'
FIND_APPLICATION = re.compile(
    b"""['"]((&#47;|/)assets(&#47;|/)application-[0-9a-f]{32}.js)['"]"""
)
FIND_AUTHORIZATION = re.compile(
    b"""['"]([0-9a-f]{32})['"].*?Authorization"""
)


def get_authorization_token():
    """ I sure am sorry about this. """
    main_page = requests.get(BASE_URL).content
    application_path = (FIND_APPLICATION.search(main_page)
                                        .groups()[0]
                                        .decode('utf8'))
    full_application_path = urljoin(BASE_URL,
                                    html.unescape((application_path)))

    application = requests.get(full_application_path).content
    token = FIND_AUTHORIZATION.search(application).groups()[0]
    return token.decode('utf8')
