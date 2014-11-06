"""
Function(s) to process different screenshot file names depending on the platform to the final unified historical name:
date time - system id - title.ext

for example:
2014.10.23 13.59.07 - xbox360 a47f16e8 - Street fighter II.png
"""

import datetime
import re
import sys


#[ CONSTANTS ]==========================================================================================================
s_DATE_FORMAT = '%Y.%m.%d'
s_TIME_FORMAT = '%H.%M.%S'
s_HISTORIC_FORMAT = '%s %s - %s %s - %s'
# todo: move satination to game database
s_SANITATION_PATTERN = r'[^\w\d \.\-_]'
#=======================================================================================================================


def raw_to_historic(s_orig_name, o_games_db):
    if o_games_db.s_name == 'xbox360':
        s_output = _xbox360_to_historic(s_orig_name, o_games_db)
    else:
        print 'ERROR: Games database not found'
        sys.exit()

    # Title sanitation
    s_output = re.sub(s_SANITATION_PATTERN, '', s_output, flags=re.I)

    return s_output


def _xbox360_to_historic(s_orig_name, o_games_db):

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

    return s_HISTORIC_FORMAT % (s_date, s_time, o_games_db.s_name, s_id, s_name)