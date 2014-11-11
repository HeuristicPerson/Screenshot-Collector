"""
Function(s) to process different screenshot file names depending on the platform to the final unified historical name:
date time - system id - title.ext

for example:
2014.10.23 13.59.07 - xbox360 a47f16e8 - Street fighter II.png
"""

import datetime
import os
import re
import sys
import cons
import gamecache

#[ CONSTANTS ]==========================================================================================================
s_DATE_FORMAT = '%Y.%m.%d'
s_TIME_FORMAT = '%H.%M.%S'
s_HISTORIC_FORMAT = '%s %s - %s %s - %s'
#=======================================================================================================================


def raw_to_historic(o_games_db, s_src_name):

    s_timestamp = s_src_name.split(' - ')[0]

    s_database = s_src_name.split(' - ')[1].split(' ')[0]
    s_scheme = s_src_name.split(' - ')[1].split(' ')[1]
    s_raw_name = ' - '.join(s_src_name.split(' - ')[2:])

    #print 'SRC: %s' % s_src_name
    #print ' DB: %s' % s_database
    #print 'SCH: %s' % s_scheme
    #print 'RAW: %s' % s_raw_name

    if s_scheme == 'freestyledash':
        ds_parsed_data = _xbox360_to_historic(s_raw_name, o_games_db)

    elif s_scheme == 'kega':
        ds_parsed_data = _kega_to_historic(s_raw_name, o_games_db)

    elif s_scheme == 'zsnes':
        ds_parsed_data = _zsnes_to_historic(s_raw_name, o_games_db)

    else:
        print 'ERROR: Unknown input scheme "%s"' % s_scheme
        sys.exit()

    # Some emulators or programs, like Freestyle Dash, include timestamp in the screenshot name that is more precise
    # than the screenshot creation date itself. In those situations, the filename parser function should provide a value
    # different than 0 in the key ds_parsed_data['f_timestamp']. So when it's present, we substitute the file timestamp
    # for the new value.
    if ds_parsed_data['f_timestamp'] != 0:
        o_date = datetime.datetime.fromtimestamp(ds_parsed_data['f_timestamp'])
        # TODO: The format for timestamp string is the same than in fentry.py. It should be a common constant somewhere.
        s_new_timestamp = o_date.strftime('%Y-%m-%d %H-%M-%S.%f')[0:-4]

        #print 'Old TS: %s' % s_timestamp
        #print 'New TS: %s' % s_new_timestamp
        #print

        s_timestamp = s_new_timestamp

    s_historic_output = '%s - %s %s - %s' % (s_timestamp, s_database, ds_parsed_data['s_id'], ds_parsed_data['s_name'])

    return s_historic_output


def _kega_to_historic(s_raw_name, o_games_db):

    s_orig_name = s_raw_name[0:-3]
    # Real name obtaining. It's safer to obtain the title in 'plain' format, limited to just a-z and 0-9 to avoid
    # conflicts with file names.
    s_id = o_games_db.get_id_by_title(s_orig_name)
    s_new_name = o_games_db.get_title_by_id(s_id, 'plain')

    return {'s_name': s_new_name, 's_id': s_id, 'f_timestamp': 0}


def _xbox360_to_historic(s_orig_name, o_games_db):
    """
    Method to rename the screenshots taken by Freestyle Dash in the xbox 360.

    :param s_orig_name: Original screenshot file name (without extension) taken by Freestyle Dash screenshot plugin.

    :param o_games_db: The database containing the correspondence between game ids and names.

    :return:
    """

    # Data read from filename
    # First the filename is completed with 0 because only milliseconds are limited to 3 characters or even less. Then,
    # The 8 character Id of the game and the timestamp are extracted separately.
    s_orig_name = s_orig_name.ljust(28, '0')
    s_id = s_orig_name[0:8].lower()
    s_orig_datetime = s_orig_name[8:]

    # Proper date-time strings generation since the file creation date is less precise than the timestamp included in
    # the file name
    o_date_time = datetime.datetime.strptime(s_orig_datetime, '%Y%m%d%H%M%S%f')

    f_timestamp = (o_date_time - datetime.datetime(1970, 1, 1)).total_seconds()

    # Real name obtaining. It's safer to obtain the title in 'plain' format, limited to just a-z and 0-9 to avoid
    # conflicts with file names.
    s_name = o_games_db.get_title_by_id(s_id, 'plain')

    return {'s_name': s_name, 's_id': s_id, 'f_timestamp': f_timestamp}


def _zsnes_to_historic(s_raw_name, o_games_db):
    """
    Function to obtain the id and filtered name for ZSNES emulator. The screenshot file name follows the pattern:

    [ROM-NAME]_001.bmp

    So, we only need to split the file name by the last underscore _ and use the left part as the game title.

    :param s_raw_name: Original file name. i.e. 'Super Mario World_001.bmp'

    :param o_games_db: Database containing the ids and names.

    :return: A dictionary with the name of the game, the id and the timestamp. For zsnes, the timestamp will be 0 since
             the screenshot pattern doesn't contain information about the timestamp.
    """

    s_rom_name = s_raw_name.rpartition('_')[0]

    s_id = o_games_db.get_id_by_title(s_rom_name)
    # After obtaining the id, it's safer to obtain the title in 'plain' format, limited to just a-z and 0-9 to avoid
    # conflicts with file names.
    s_new_name = o_games_db.get_title_by_id(s_id, 'plain')

    return {'s_name': s_new_name, 's_id': s_id, 'f_timestamp': 0}