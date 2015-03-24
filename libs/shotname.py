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
u_DATE_FORMAT = u'%Y.%m.%d'
u_TIME_FORMAT = u'%H.%M.%S'
u_HISTORIC_FORMAT = u'%s %s - %s %s - %s'
#=======================================================================================================================


def raw_to_historic(o_games_db, u_src_name):
    """
    Function to convert a **COLLECTED** screenshot name to the **FINAL** historical naming scheme used by Screenshot
    Collector.

    Remember:

        1. Screenshots in the original source are in naming scheme defined by the emulator that took them.

        2. BUT when the screenshots are downloaded to the computer running Screenshot Collector, IMMEDIATELY are renamed
           to [REMOTE_FILE_HUMAN_DATE] - [DB_NAME] [SOURCE_SCHEME] - [REMOTE_FILE_NAME]

    For example:

        From: Super Mario World (USA).png

          To: 2014-10-31 19-07-41.00 - snes zsnes - Super Mario World (USA).png

    You can see all the details in "shotsource.py", in the method "download_files(self, s_dst_dir)" from "ShotSource"
    class.

    :param o_games_db: Database object containing the pairs unique identifier (CRC32 - Real name).

    :param u_src_name: Original emulator screenshot name.

    :return:
    """

    u_timestamp = u_src_name.split(u' - ')[0]

    u_database = u_src_name.split(u' - ')[1].split(u' ')[0]
    u_scheme = u_src_name.split(u' - ')[1].split(u' ')[1]
    u_raw_name = u' - '.join(u_src_name.split(u' - ')[2:])

    if u_database != o_games_db.u_name:
        print '\nWARNING!!!'
        print
        print 'You are attempting to check a file with the DB indicator "%s":' % u_database
        print
        print '    %s' % u_src_name.encode('ascii', 'strict')
        print
        print 'Using the DB "%s". Both are different!!!' % o_games_db.u_name
        print
        print 'The most common reason for this is Screenshot Collector was interrupted in the'
        print 'past when it was running.So, now you have screenshots coming from different'
        print 'sources in your temporary historic folder:'
        print
        print '    %s' % cons.u_TEMP_COLLECT_DIR.encode('ascii', 'strict')
        print
        print 'To avoid losing your precious screenshots, move them to a different place.'

        sys.exit()

    if u_scheme == u'freestyledash':
        dx_parsed_data = _xbox360_to_historic(u_raw_name, o_games_db)

    elif u_scheme == u'kega':
        dx_parsed_data = _kega_to_historic(u_raw_name, o_games_db)

    elif u_scheme == u'libretroplus':
        dx_parsed_data = _libretro_plus(u_raw_name, o_games_db)

    elif u_scheme == u'zsnes':
        dx_parsed_data = _zsnes_to_historic(u_raw_name, o_games_db)

    else:
        raise Exception('ERROR: Unknown input scheme "%s"' % u_scheme.encode(u'ascii', u'strict'))

    # TODO: Maybe I should delete this piece of code since I think I'm too picky about the creation date of screenshots.
    # Some emulators or programs, like Freestyle Dash, include timestamp in the screenshot name that is more precise
    # than the screenshot creation date itself. In those situations, the filename parser function should provide a value
    # different than 0 in the key dx_parsed_data['f_timestamp']. So when it's present, we substitute the file timestamp
    # for the new value.
    if dx_parsed_data[u'f_timestamp'] != 0:
        o_date = datetime.datetime.fromtimestamp(dx_parsed_data[u'f_timestamp'])
        # TODO: The format for timestamp string is the same than in fentry.py. It should be a common constant somewhere.
        s_new_timestamp = o_date.strftime(u'%Y-%m-%d %H-%M-%S.%f')[0:-4]

        #print 'Old TS: %s' % u_timestamp
        #print 'New TS: %s' % s_new_timestamp
        #print

        u_timestamp = s_new_timestamp

    # If the id doesn't exist in the DB, the o_games_db tries to use an online scrapper which only works for xbox360. In
    # other case it returns "________" which, for our purposes means, Title not present in DB and Title not available
    # online. So the best we can do is to keep the name provided by the emulator. The Id is already going to be
    # "________" so it's easy to keep track of the unknown games in the historical screenshot folder and the emulator
    # name is a *good* aproximation to the official title of the game.
    if dx_parsed_data['u_name'] == u'________':
        dx_parsed_data['u_name'] = gamecache.sanitize(u_raw_name, u'plain')

    u_historic_output = u'%s - %s %s - %s' % (u_timestamp,
                                              u_database,
                                              dx_parsed_data[u'u_id'],
                                              dx_parsed_data[u'u_name'])

    return u_historic_output


def _kega_to_historic(u_orig_name, o_games_db):
    """
    Function to convert screenshots coming from Kega Fusion (http://segaretro.org/Kega_Fusion).

    :param u_orig_name: Original screenshot file name (without extension) taken by Kega Fusion
    
    :param o_games_db: Database containing the correspondence between real names and id (CRC32).

    :return: A dictionary with the name of the game, the id and the timestamp. For Kega, the timestamp will be 0 since
             the screenshot pattern doesn't contain information about the timestamp. 
    """

    s_orig_name = u_orig_name[0:-3]
    # Real name obtaining. It's safer to obtain the title in 'plain' format, limited to just a-z and 0-9 to avoid
    # conflicts with file names.
    s_id = o_games_db.get_id_by_title(s_orig_name)
    u_new_name = o_games_db.get_title_by_id(s_id, u'plain')

    return {u'u_name': u_new_name, u'u_id': s_id, u'f_timestamp': 0}


def _libretro_plus(u_orig_name, o_games_db):
    """
    Function to convert screenshots coming from LibRetro Plus. (NOTE! this is not the real Libretro screenshot naming
    convention but my OWN naming convention.
    
    By now (22 March 2015), Libretro doesn't save screenshots including the name of the ROM so it's impossible to use it
    with Screenshot Collector. To solve that issue, and others, I created my own launching script for LibRetro which,
    among other features, renames the screenshot to "[ROM] - [SECONDS FROM EPOCH].[NANOSECONDS].png"

    :param u_orig_name: Original screenshot file name (without extension) taken by LibRetro PLUS (not the real one, my
                        own launching script). i.e.
                        "Super Mario World (USA) - 1257897564866856.124578987.png"
    
    :param o_games_db: Database containing the correspondence between real names and id (CRC32).

    :return: A dictionary with the name of the game, the id and the timestamp. For Kega, the timestamp will be 0 since
             the screenshot pattern doesn't contain information about the timestamp. 
    """
    
    # First we discard the part after the rom name. The timestamp is TOTALLY useless since it's the time when the
    # screenshot was renamed to this scheme, NOT the time when it was taken.
    u_orig_name = u_orig_name.rpartition(' - ')[0]
    
    u_id = o_games_db.get_id_by_title(u_orig_name)

    # We already have the name of the ROM but it's safer to re-obtain it from the Database a) to have a clean name
    # avoiding weird characters, and b) to have it converted to lowercase and so on. Maybe this double check is not good
    # in terms of performance but I think it's much safer.
    u_new_name = o_games_db.get_title_by_id(u_id, u'plain')
    
    return {u'u_name': u_new_name, u'u_id': u_id, u'f_timestamp': 0}
    

def _xbox360_to_historic(u_orig_name, o_games_db):
    """
    Method to rename the screenshots taken by Freestyle Dash in the xbox 360.

    :param u_orig_name: Original screenshot file name (without extension) taken by Freestyle Dash screenshot plugin.

    :param o_games_db: The database containing the correspondence between game ids and names.

    :return: A dictionary with the name of the game, the id and the timestamp.
    """

    # Data read from filename
    # First the filename is completed with 0 because only milliseconds are limited to 3 characters or even less. Then,
    # The 8 character Id of the game and the timestamp are extracted separately.
    u_orig_name = u_orig_name.ljust(28, u'0')
    u_id = u_orig_name[0:8].lower()
    u_orig_datetime = u_orig_name[8:]

    # Proper date-time strings generation since the file creation date is less precise than the timestamp included in
    # the file name
    o_date_time = datetime.datetime.strptime(u_orig_datetime, u'%Y%m%d%H%M%S%f')

    f_timestamp = (o_date_time - datetime.datetime(1970, 1, 1)).total_seconds()

    # Real name obtaining. It's safer to obtain the title in 'plain' format, limited to just a-z and 0-9 to avoid
    # conflicts with file names.
    u_name = o_games_db.get_title_by_id(u_id, u'plain')

    return {u'u_name': u_name, u'u_id': u_id, u'f_timestamp': f_timestamp}


def _zsnes_to_historic(u_raw_name, o_games_db):
    """
    Function to obtain the id and filtered name for ZSNES emulator. The screenshot file name follows the pattern:

    [ROM-NAME]_001.bmp

    So, we only need to split the file name by the last underscore _ and use the left part as the game title.

    :param u_raw_name: Original file name. i.e. 'Super Mario World_001.bmp'

    :param o_games_db: Database containing the ids and names.

    :return: A dictionary with the name of the game, the id and the timestamp. For zsnes, the timestamp will be 0 since
             the screenshot pattern doesn't contain information about the timestamp.
    """

    u_rom_name = u_raw_name.rpartition(u'_')[0]

    u_id = o_games_db.get_id_by_title(u_rom_name)
    # After obtaining the id, it's safer to obtain the title in 'plain' format, limited to just a-z and 0-9 to avoid
    # conflicts with file names.
    u_new_name = o_games_db.get_title_by_id(u_id, u'plain')

    return {u'u_name': u_new_name, u'u_id': u_id, u'f_timestamp': 0}