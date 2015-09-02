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

import argparse
import fcntl
import os
import sys

u_CWD = os.path.dirname(os.path.realpath(__file__))
sys.path.append(u_CWD)

from libs import ini
from libs import log
from libs import scr
from libs import shotsource

# Constants ============================================================================================================
u_CFG_INI = os.path.join(u_CWD, 'config.ini')
u_LOG_FILE = os.path.join(u_CWD, 'collector.log')
#-----------------------------------------------------------------------------------------------------------------------

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


def get_cmdline_options():
    """
    Function to process the commandline options.

    :return: Todo: decide.
    """

    # Creation of the parameter options
    o_arg_parser = argparse.ArgumentParser()
    o_arg_parser.add_argument('-l',
                              action='store_true',
                              help='Activate program logging (writing information to file after each run)')

    o_args = o_arg_parser.parse_args()

    # To log or not to log, that's the question
    if o_args.l:
        b_logging = True
    else:
        b_logging = False

    return b_logging


def read_collector_config(u_file):
    """
    Function to read the main configuration for the collector tool from disk.
    :param s_file:
    :return:
    """

    o_ini = ini.ParsedIni()
    o_ini.load_from_disk(u_file)

    u_temp_dir = o_ini.get_param('collector', 'temp_dir')
    u_hist_dir = o_ini.get_param('collector', 'hist_dir')
    u_hist_ext = o_ini.get_param('collector', 'hist_ext')

    if not os.path.isdir(u_temp_dir):
        print 'Temporary collector directory doesn\'t exist:'
        print '   %s' % u_temp_dir.encode('utf8', 'strict')
        sys.exit()

    if not os.path.isdir(u_hist_dir):
        print 'Historic directory doesnt\'t exist:'
        print '    %s' % u_hist_dir.encode('utf8', 'strict')
        sys.exit()

    return u_temp_dir, u_hist_dir, u_hist_ext


def read_sources_config(s_file):
    """
    Function to load the
    :param s_file:
    :return:
    """

    o_ini = ini.ParsedIni()
    o_ini.load_from_disk(s_file)

    u_hist_ext = o_ini.get_param('collector', 'hist_ext')

    # Reading sources configuration
    lo_sources = []

    for o_section in o_ini:
        # Source sections of the ini contain a number, i.e. [source 1]. So we need to check if the 1st part is source
        # before obtaining the data
        u_section_type = o_section.u_name.split(' ')[0]

        if u_section_type == u'source':

            # Obtaining information from parsed ini file
            u_type = o_ini.get_param(o_section.u_name, u'type')
            if u_type not in (u'dir', u'ftp', u'smb'):
                raise Exception('config.ini error: unknown or missing source type "%s"'
                                % u_type.encode('ascii', 'strict'))

            u_address = o_ini.get_param(o_section.u_name, u'address')
            if u_address == u'':
                raise Exception('config.ini error: unknown or missing address "%s"'
                                % u_address.encode('ascii', 'strict'))

            u_root = o_ini.get_param(o_section.u_name, u'root')
            u_user = o_ini.get_param(o_section.u_name, u'user')
            u_password = o_ini.get_param(o_section.u_name, u'password')

            u_database = o_ini.get_param(o_section.u_name, u'database')
            if u_database == u'':
                raise Exception('config.ini error: unknown or missing database "%s"'
                                % u_database.encode('ascii', 'strict'))

            u_scrapper = o_ini.get_param(o_section.u_name, u'scrapper')

            u_scheme = o_ini.get_param(o_section.u_name, u'scheme')
            if u_scheme == u'':
                raise Exception('config.ini error: unknown or missing database "%s"'
                                % u_scheme.encode('ascii', 'strict'))

            lu_get_exts = ini.list_str(o_ini.get_param(o_section.u_name, u'get_exts'))
            if len(lu_get_exts) == 0:
                raise Exception('config.ini warning: not getting any extension from source "%s"'
                                % o_section.u_name)

            lu_del_exts = ini.list_str(o_ini.get_param(o_section.u_name, u'del_exts'))

            u_recursive = o_ini.get_param(o_section.u_name, u'recursive')
            if u_recursive.lower() in ('yes', 'true', '1'):
                b_recursive = True
            else:
                b_recursive = False

            u_clean = o_ini.get_param(o_section.u_name, u'clean_dirs')
            if u_clean.lower() in ('yes', 'true', '1'):
                b_clean = True
            else:
                b_clean = True

            # With all the required data, the source can be configured
            o_source = shotsource.ShotSource(o_ini.get_param(o_section.u_name, u'name'))

            o_source.u_hist_ext = u_hist_ext                    # Historical extension

            o_source.set_source(u_type, u_address, u_root)      # Type of source, address, and root folder
            o_source.set_user_pass(u_user, u_password)          # User and pass for FTP or SAMBA

            o_source.set_db_and_scheme(u_database, u_scheme)    # Name of the DB and source screenshot scheme
            o_source.u_scrapper = u_scrapper                    # Scrapper to use in case the id is not found
            o_source.set_get_exts(*lu_get_exts)                 # File extensions to download_file from source
            o_source.set_del_exts(*lu_del_exts)                 # File extensions to remove from source

            if b_recursive:                                     # Searching for images recursively
                o_source.set_recursive()
            if b_clean:
                o_source.set_clean_dirs()

            lo_sources.append(o_source)

    return lo_sources


# Main code
#=======================================================================================================================
scr.printh(u'Screenshot Collector v0.2', 1)

if not is_file_locked('.lock'):
    print 'Script already running'
    sys.exit()

b_logging = get_cmdline_options()

if b_logging:
    o_log = log.Log(u_LOG_FILE)
    o_log.log('STARTING COLLECTOR')
else:
    o_log = None

# TODO: add command line parameters to allow the user to run the collector for just one system.
# Apart from for testing purposes, it'll be also helpful to solve issues with mixed screenshots in the temporary
# collection folder.

u_temp_dir, u_hist_dir, u_hist_ext = read_collector_config(u_CFG_INI)

lo_shot_sources = read_sources_config(u_CFG_INI)

for o_shot_source in lo_shot_sources:
    u_message = 'SOURCE: %s (%s, %s)' % (o_shot_source.u_name,
                                         o_shot_source.u_type,
                                         o_shot_source.u_host)
    scr.printh(u_message, 1)

    o_shot_source.download_files(u_temp_dir, o_log)
    o_shot_source.archive_files(u_temp_dir, u_hist_dir, o_log)

if o_log:
    o_log.close()