import fcntl
import os
import sys

from libs import cons
from libs import shotsource


# Configuration - Basics
#=======================================================================================================================
#s_TEMP_DIR = 'images/temp'              # Directory for temporal files
#s_HIST_DIR = 'images/historic'          # Directory for historic images
#s_HIST_EXT = 'png'                      # Historical images extension (typically png for quality or jpg for low size)
#s_DAT_DIR = 'dats'                      # Directory containing Id/Title dat files


# Configuration - FTPs
#=======================================================================================================================
lo_shot_sources = []

# Xbox 360 FTP configuration
#o_shot_source_xbox360 = shotsource.ShotSource('Xbox 360')
#
#o_shot_source_xbox360.set_source('ftp', '192.168.0.106', '/Hdd1/Freestyle Dash/Plugins/UserData')
#o_shot_source_xbox360.set_user_pass('xbox', 'xbox')                     # User and pass for FTP or SAMBA
#
#o_shot_source_xbox360.set_db_and_scheme('xbox360', 'xbox360')           # Name of the DB and source screenshot scheme
#o_shot_source_xbox360.set_get_exts('bmp')                               # File extensions to download_file from source
#o_shot_source_xbox360.set_del_exts('bmp', 'meta')                       # File extensions to remove from source
#o_shot_source_xbox360.set_recursive()                                   # Searching for images recursively
#o_shot_source_xbox360.set_clean_dirs()                                  # Image folders are deleted (if empty)
#
#lo_shot_sources.append(o_shot_source_xbox360)

# zsnes dir configuration
o_shot_source_snes = shotsource.ShotSource('Super Nintendo')

o_shot_source_snes.set_source('dir', 'localhost', '/home/david/.zsnes')

o_shot_source_snes.set_db_and_scheme('snes', 'zsnes')                   # Name of this cfg (used for DB and renaming)
o_shot_source_snes.set_get_exts('bmp')                                  # File extensions to download_file from source
o_shot_source_snes.set_del_exts()                                       # File extensions to remove from source

lo_shot_sources.append(o_shot_source_snes)

# Helper function to avoid multiple instances of the script
#=======================================================================================================================
o_lock_file = None


def is_file_locked(s_file):
    global o_lock_file

    o_lock_file = open(s_file, 'w')

    try:
        fcntl.lockf(o_lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return False

    return True


# Main code
#=======================================================================================================================
print 'Screenshot gatherer v0.1'
print '%s\n' % ('=' * 78)

if not is_file_locked('.lock'):
    print 'Script already running'
    sys.exit()

for o_shot_source in lo_shot_sources:
    o_shot_source.download_files(cons.s_TEMP_DIR)
    #o_shot_source.archive_files(cons.s_TEMP_DIR, cons.s_HIST_DIR)