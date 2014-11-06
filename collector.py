import fcntl
import os
import sys

from libs import shotsource


# Configuration - Basics
#=======================================================================================================================
s_TEMP_DIR = 'images/temp'              # Directory for temporal files
s_HIST_DIR = 'images/historic'          # Directory for historic images
s_HIST_EXT = 'png'                      # Historical images extension (typically png for quality or jpg for low size)
s_DAT_DIR = 'dats'                      # Directory containing Id/Title dat files


# Configuration - FTPs
#=======================================================================================================================
lo_shot_sources = []

# Xbox 360 FTP configuration
o_shot_source_xbox360 = shotsource.ShotSource()
o_shot_source_xbox360.s_name = 'xbox360'                                # Name of this cfg (used for DB and renaming)
o_shot_source_xbox360.s_type = 'ftp'                                    # Type of source ('ftp', 'samba', 'dir')
o_shot_source_xbox360.s_host = '192.168.0.106'                          # Address of the FTP
o_shot_source_xbox360.s_user = 'xbox'                                   # User for the FTP
o_shot_source_xbox360.s_pass = 'xbox'                                   # Password for the FTP
o_shot_source_xbox360.s_root = '/Hdd1/Freestyle Dash/Plugins/UserData'  # Folder where to search for images
o_shot_source_xbox360.ls_get_exts = ('bmp')                             # File extensions to download_file from source
o_shot_source_xbox360.ls_del_exts = ('bmp', 'meta')                     # File extensions to remove from source
o_shot_source_xbox360.b_recursive = True                                # Searching for images recursively
o_shot_source_xbox360.b_dir_keep = False                                # Image folders are deleted (if empty)
lo_shot_sources.append(o_shot_source_xbox360)

# zsnes dir configuration
o_shot_source_zsnes = shotsource.ShotSource()
o_shot_source_zsnes.s_name = 'snes'                                      # Name of this cfg (used for DB and renaming)
o_shot_source_zsnes.s_type = 'dir'                                       # Type of source ('ftp', 'samba', 'dir')
o_shot_source_zsnes.s_host = 'localhost'                                 # Address of the FTP
o_shot_source_zsnes.s_user = ''                                          # User for the FTP
o_shot_source_zsnes.s_pass = ''                                          # Password for the FTP
o_shot_source_zsnes.s_root = '/home/david/PycharmProjects/screenshotcollector/images'                        # Folder where to search for images
o_shot_source_zsnes.ls_get_exts = ('bmp')                                # File extensions to download_file from source
o_shot_source_zsnes.ls_del_exts = ()                                     # File extensions to remove from source
o_shot_source_zsnes.b_recursive = True                                  # Searching for images recursively
o_shot_source_zsnes.b_dir_keep = False                                   # Image folders are deleted (if empty)
lo_shot_sources.append(o_shot_source_zsnes)

# Default values overriding
s_cwd = os.path.dirname(os.path.realpath(__file__))

for o_src_wrapper in lo_shot_sources:
    o_src_wrapper.s_hist_ext = s_HIST_EXT
    o_src_wrapper.find_dat_file(os.path.join(s_cwd, s_DAT_DIR))


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
print '========================'

if not is_file_locked('.lock'):
    print 'Script already running'
    sys.exit()

for o_shot_source in lo_shot_sources:
    o_shot_source.download_files(s_TEMP_DIR)
    o_shot_source.archive(s_TEMP_DIR, s_HIST_DIR)