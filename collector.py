#!/usr/local/bin/python
# -*- coding: utf8 -*-

"""
Script to build a mosaic of images containing all the screenshots of the previous period of time. Imagine we are working
on a daily basis, so the previous period of time is yesterday. If we were working in a monthly basis and we were in
April, the previous period of time would be March.

The mosaic can be configured using constants defined in 'libs/cons.py'. Basically, the options allow you to change the
periodicity (daily, weekly, monthly, yearly), the background color, the font size and font color of the main heading and
screenshot footer.
"""


import fcntl
import sys

from libs import cons
from libs import ini
from libs import shotsource


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


def read_sources_config(s_file):
    """
    Function to load the
    :param s_file:
    :return:
    """

    o_ini = ini.ParsedIni(s_file)

    # Reading sources configuration
    lo_sources = []

    for dx_section in o_ini:
        s_section = dx_section['section'].split(' ')[0]
        ds_values = dx_section['values']
        if s_section == 'source':

            # Obtaining information from parsed ini file
            s_type = ds_values.get('type', '')
            if s_type not in ('dir', 'ftp', 'smb'):
                print 'config.ini error: unknown or missing source type "%s"' % s_type
                sys.exit()

            s_address = ds_values.get('address', '')
            if s_address == '':
                print 'config.ini error: unknown or missing address "%s"' % s_address
                sys.exit()

            s_root = ds_values.get('root', '')

            s_user = ds_values.get('user', '')

            s_password = ds_values.get('password', '')

            s_database = ds_values.get('database', '')
            if s_database == '':
                print 'config.ini error: unknown or missing database "%s"' % s_database
                sys.exit()

            s_scheme = ds_values.get('scheme', '')
            if s_scheme == '':
                print 'config.ini error: unknown or missing database "%s"' % s_scheme
                sys.exit()

            ls_get_exts = ini.list_str(ds_values.get('get_exts', ''))
            if len(ls_get_exts) == 0:
                print 'config.ini warning: not getting any extension from source "%s"' % dx_section['section']

            ls_del_exts = ini.list_str(ds_values.get('del_exts', ''))

            s_recursive = ds_values.get('recursive', '')
            if s_recursive.lower() in ('yes', 'true', '1'):
                b_recursive = True
            else:
                b_recursive = False

            s_clean = ds_values.get('clean_dirs', '')
            if s_recursive.lower() in ('yes', 'true', '1'):
                b_clean = True
            else:
                b_clean = True

            # With all the required data, the source can be configured
            o_source = shotsource.ShotSource(ds_values.get('name', dx_section['section']))

            o_source.set_source(s_type, s_address, s_root)
            o_source.set_user_pass(s_user, s_password)         # User and pass for FTP or SAMBA

            o_source.set_db_and_scheme(s_database, s_scheme)   # Name of the DB and source screenshot scheme
            o_source.set_get_exts(*ls_get_exts)                 # File extensions to download_file from source
            o_source.set_del_exts(*ls_del_exts)                 # File extensions to remove from source
            if b_recursive:
                o_source.set_recursive()                       # Searching for images recursively
            if b_clean:
                o_source.set_clean_dirs()

            lo_sources.append(o_source)

    return lo_sources


# Main code
#=======================================================================================================================
print 'Screenshot gatherer v0.1'
print '%s\n' % ('=' * 78)

if not is_file_locked('.lock'):
    print 'Script already running'
    sys.exit()

lo_shot_sources = read_sources_config('config.ini')

for o_shot_source in lo_shot_sources:
    o_shot_source.download_files(cons.s_TEMP_COLLECT_DIR)
    o_shot_source.archive_files(cons.s_TEMP_COLLECT_DIR, cons.s_HIST_DIR)