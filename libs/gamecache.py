import os
import re
import sys

import fentry
import xcrapper

# Constants
#=======================================================================================================================
s_SANITATION_PATTERN = r'[^\w\d \.\-_]'


class Database:
    def __init__(self, u_cache_file):
        self._du_entries = {}
        self._u_header = ''

        if not os.path.isfile(u_cache_file.encode('utf8', 'strict')):
            print 'ERROR: Can\'t load database. File "%s" doesn\'t exist.' % u_cache_file.encode('utf8', 'strict')
            sys.exit()

        self._u_cache_file = u_cache_file
        self._load_data()

        # Database name from cache file using fentry library. Probably a bit overdone...
        o_cache_file = fentry.FileEntry()
        o_cache_file.from_local_path(u_cache_file)

        self.u_name = o_cache_file.u_name

    def _load_data(self):
        """
        Method to read all the cached information (id and title) from the offline database.

        :return: Nothing
        """

        o_file = open(self._u_cache_file, 'r')

        b_header_mode = True
        s_header = ''

        for s_line in o_file:
            s_line_clean = s_line.strip()

            # Parsing the header
            if b_header_mode:
                if len(s_line_clean) != 0 and s_line_clean[0] == '#':
                    s_header += s_line
                else:
                    b_header_mode = False
                    self._u_header = s_header.decode('utf8')

            # Parsing the content
            else:
                if len(s_line_clean) != 0 and s_line[0] != '#':
                    s_id = s_line_clean.partition('\t')[0]
                    s_title = s_line_clean.partition('\t')[2]

                    self._du_entries[s_id] = s_title.decode('utf8')

        o_file.close()

    def _write_data(self):
        """
        Method to save the cached database to disk.

        :return: Nothing
        """

        ld_data_elements = []

        for s_key, s_value in self._du_entries.iteritems():
            d_data_element = {'id': s_key, 'title': s_value}
            ld_data_elements.append(d_data_element)

        ld_data_elements = sorted(ld_data_elements, key=lambda d_data_element: d_data_element['title'])

        o_file = open(self._u_cache_file, 'w')

        o_file.write(self._u_header.encode('utf8', 'ignore'))

        for d_data_element in ld_data_elements:
            u_line = u'%s\t%s\n' % (d_data_element['id'], d_data_element['title'])
            o_file.write(u_line.encode('utf8', 'strict'))

        o_file.close()

    def get_title_by_id(self, u_id, u_sanitation='raw'):
        """
        Method to obtain the title of a game from its id. In case the selected id doesn't appear in the database, the
        title is searched in an online web page using the right scrapper selected by the name of the database*.

        * This online search feature actually is just active for Xbox360 games so far.

        :param u_id: id to search.
        :param s_sanitation: sanitation method to use with the title. 'raw' original UTF8 title; 'ascii' title is
                             downgraded to ascii code deleting all the unrecognized symbols

        :return: A string containing the title of the game
        """

        u_id = u_id.strip()

        try:
            u_title = self._du_entries[u_id]

        except KeyError:
            u_title = xcrapper.get_title_by_id(self.u_name, u_id)

            # TODO: I don't want to add empty entries in my database
            self._du_entries[u_id] = u_title
            self._write_data()

        u_title = sanitize(u_title, u_sanitation)

        return u_title.strip()

    def get_id_by_title(self, u_title):
        """
        Method to check for the ID of a game in the database from it's name.

        :param u_title: Title of the game to check. i.e. "Super Mario World (USA)"

        :return: The unique identifier of the game. i.e. "123ab98f". If the title is not found in the DB, "________" is
                 returned instead.
        """

        u_id = '________'

        for s_db_id, s_db_title in self._du_entries.iteritems():
            if s_db_title == u_title:
                u_id = s_db_id
                break

        return u_id

    def get_items(self):
        return len(self._du_entries)


def sanitize(u_src_title, u_method):
    """
    Method to sanitize titles.
    :param u_src_title:
    :param u_method:
    :return:
    """
    if u_method == u'ascii':
        u_dst_title = u_src_title.encode('ascii', 'ignore')

    elif u_method == u'plain':
        u_dst_title = re.sub(s_SANITATION_PATTERN, '', u_src_title, flags=re.I)
        u_dst_title = u_dst_title.encode('ascii', 'ignore').lower()

    elif u_method == u'raw':
        u_dst_title = u_src_title

    else:
        raise Exception('Unknown sanitize method "%s"' % u_method.encode('ascii', 'strict'))

    return u_dst_title.strip()