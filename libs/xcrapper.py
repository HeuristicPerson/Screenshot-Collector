"""
Simple library to retrieve real game titles from game ids using the marketplace website.
========================================================================================================================

The url of each game in the marketplace included the game id in the last 8 characters (take a look at s_URL_TEMPLATE).
So, it's really simple to obtain the real game title obtaining the web page and reading the title from the first, and
only, h1 element.
"""

import requests
import lxml.html

s_URL_TEMPLATE = 'http://marketplace.xbox.com/en-US/Product/Super-Meat-Boy/66acd000-77fe-1000-9115-d802{GAME_ID}'


def id_to_title(s_id):
    if s_id == '00000000':
        s_title = 'Freestyle Dash'

    else:
        s_url = s_URL_TEMPLATE.replace('{GAME_ID}', s_id)

        o_page = requests.get(s_url)
        o_tree = lxml.html.fromstring(o_page.text)

        s_title = o_tree.xpath('//h1/text()')[0]

        # To avoid the unknown game error
        if s_title[0:6] == 'Ooops!':
            s_title = '--- Unknown game ---'

    return s_title