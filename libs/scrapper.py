"""
Simple library to retrieve real game titles from game ids using the marketplace website.
========================================================================================================================

The url of each game in the marketplace included the game id in the last 8 characters (take a look at s_URL_TEMPLATE).
So, it's really simple to obtain the real game title obtaining the web page and reading the title from the first, and
only, h1 element.
"""

import requests
import lxml.html


def get_title_by_id(u_scrapper, u_id):

    if u_scrapper == u'xbox360':
        u_output = _xbox360(u_id)

    else:
        raise Exception('Unknown scrapper "%s"' % u_scrapper)

    return u_output


def _xbox360(u_id):
    """
    Function to obtain a game's title from xbox.com from its 8 character hexadecimal id.

    :param u_id: The id of the game. i.e.
    :return:
    """

    u_URL_TEMPLATE = u'http://marketplace.xbox.com/en-US/Product/66acd000-77fe-1000-9115-d802{GAME_ID}'

    if u_id == u'00000000':
        u_title = u'Freestyle Dash'

    else:
        s_url = u_URL_TEMPLATE.replace(u'{GAME_ID}', u_id)

        o_page = requests.get(s_url)
        o_tree = lxml.html.fromstring(o_page.text)

        u_scrapped_title = o_tree.xpath(u'//div[@id="gameDetails"]/h1/text()')[0].strip()

        # To avoid the unknown game error
        if u_scrapped_title[0:6] == u'Ooops!':
            u_title = u'-- Unknown game --'
        elif u_scrapped_title == '':
            u_title = u'-- Nothing Scrapped --'
        else:
            u_title = u_scrapped_title

    return u_title