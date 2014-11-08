import os
import sys

import fentry
import xcrapper


class Database:
    def __init__(self, s_cache_file):
        self._ds_entries = {}
        self._s_header = ''

        if not os.path.isfile(s_cache_file):
            print 'ERROR: Can\'t load database. File "%s" doesn\'t exist.' % s_cache_file
            sys.exit()

        self._s_cache_file = s_cache_file
        self._load_data()

        # Database name from cache file using fentry library. Probably a bit overdone...
        o_cache_file = fentry.FileEntry()
        o_cache_file.from_local_path(s_cache_file)

        self._s_name = o_cache_file.s_name


    def _load_data(self):
        """
        Method to read all the cached information (id and title) from the offline database.

        :return: Nothing
        """

        o_file = open(self._s_cache_file, 'r')

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
                    self._s_header = s_header.decode('utf8')

            # Parsing the content
            else:
                if len(s_line_clean) != 0 and s_line[0] != '#':
                    s_id = s_line_clean.partition('\t')[0]
                    s_title = s_line_clean.partition('\t')[2]

                    self._ds_entries[s_id] = s_title.decode('utf8')

        o_file.close()

    def _write_data(self):
        """
        Method to save the cached database to disk.

        :return: Nothing
        """

        ld_data_elements = []

        for s_key, s_value in self._ds_entries.iteritems():
            d_data_element = {'id': s_key, 'title': s_value}
            ld_data_elements.append(d_data_element)

        ld_data_elements = sorted(ld_data_elements, key=lambda d_data_element: d_data_element['title'])

        o_file = open(self._s_cache_file, 'w')

        o_file.write(self._s_header.encode('utf8', 'ignore'))

        for d_data_element in ld_data_elements:
            o_file.write('%s\t%s\n' % (d_data_element['id'], d_data_element['title'].encode('utf8', 'ignore')))

        o_file.close()

    def get_title_by_id(self, s_id, s_sanitation='raw'):

        s_id = s_id.strip()

        try:
            s_title = self._ds_entries[s_id]

        except KeyError:
            s_title = xcrapper.get_title_by_id(self._s_name, s_id)

            self._ds_entries[s_id] = s_title
            self._write_data()

        return s_title

    def get_id_by_title(self, s_title):

        s_id = '________'

        for s_db_id, s_db_title in self._ds_entries.iteritems():
            if s_db_title == s_title:
                s_id = s_db_id
                break

        return s_id

    def get_items(self):
        return len(self._ds_entries)