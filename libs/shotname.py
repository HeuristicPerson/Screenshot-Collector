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
# todo: move sanitation to game database
s_SANITATION_PATTERN = r'[^\w\d \.\-_]'  # To avoid problems with the archive file name we clean "weird" characters
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

    s_historic_output = '%s - %s %s - %s' % (s_timestamp, s_database, ds_parsed_data['s_id'], ds_parsed_data['s_name'])

#    # Title sanitation
#    s_output = re.sub(s_SANITATION_PATTERN, '', s_output, flags=re.I)
#
    return s_historic_output


def _kega_to_historic(s_raw_name, o_games_db):
    pass
    s_orig_name = s_raw_name[0:-3]
    s_id = o_games_db.get_id_by_title(s_orig_name)

    return {'s_name': s_orig_name, 's_id': s_id, 'f_timestamp': 0}


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

    # Proper date-time strings generation
    o_date_time = datetime.datetime.strptime(s_orig_datetime, '%Y%m%d%H%M%S%f')

    o_date = o_date_time.date()
    s_date = o_date.strftime(s_DATE_FORMAT)

    o_time = o_date_time.time()
    s_time = o_time.strftime(s_TIME_FORMAT)

    # Real name obtaining
    s_name = o_games_db.get_title_by_id(s_id)

    return {'s_name': s_name, 's_id': s_id, 'f_timestamp': 0}


def _zsnes_to_historic(s_raw_name, o_games_db):
    s_rom_name = s_raw_name.rpartition('_')[0]

    s_id = o_games_db.get_id_by_title(s_rom_name)

    return {'s_name': s_rom_name, 's_id': s_id, 'f_timestamp': 0}