#!/usr/local/bin/python
# -*- coding: utf8 -*-

import argparse
import datetime
import locale
import os
import shutil
import sys

from libs import cons
from libs import gamecache
from libs import fileutils

locale.setlocale(locale.LC_ALL, 'es_ES.utf8')


# Helper functions
#=======================================================================================================================
def get_datetime_range(o_datetime, u_period):
    """
    Function to build the date-stamp of the previous time section. i.e. If we were working with a weekly periodicity and
    we were in the week 30 of the year 2014, the previous timestamp would be 2014-29.

    :return: s_timestamp: A string representing a timestamp. i.e. '2014-29'.

    :return: s_date_format: A string representing the pattern for the timestamp. i.e. '%Y-%U'
    """

    #o_date_now = datetime.datetime.now()

    # Grouping name configuration to create the mosaics and to check previous states
    if u_period == u'day':
        o_yesterday = o_datetime - datetime.timedelta(days=1)
        o_start = datetime.datetime(o_yesterday.year, o_yesterday.month, o_yesterday.day, 0, 0, 0, 0)
        o_end = datetime.datetime(o_yesterday.year, o_yesterday.month, o_yesterday.day, 23, 59, 59, 999999)

    elif u_period == u'week':
        o_last_monday = o_datetime - datetime.timedelta(o_datetime.isoweekday() + 6)
        o_last_sunday = o_last_monday + datetime.timedelta(6)
        o_start = datetime.datetime(o_last_monday.year, o_last_monday.month, o_last_monday.day, 0, 0, 0, 0)
        o_end = datetime.datetime(o_last_sunday.year, o_last_sunday.month, o_last_sunday.day, 23, 59, 59, 999999)

    elif u_period == u'month':
        o_start = datetime.datetime(o_datetime.year, o_datetime.month - 1, 1, 0, 0, 0, 0)
        o_end_day = o_datetime - datetime.timedelta(days=o_datetime.day)
        o_end = datetime.datetime(o_end_day.year, o_end_day.month, o_end_day.day, 23, 59, 59, 999999)

    elif u_period == u'year':
        o_start = datetime.datetime(o_datetime.year - 1, 1, 1, 0, 0, 0, 0)
        o_end = datetime.datetime(o_datetime.year - 1, 12, 31, 23, 59, 59, 999999)

    elif u_period == u'all':
        # A bit messy but instead of manually setting a wide enough start and finish dates, it's much better to get the
        # real oldest and newest dates from files stored in the historic folder. Later we can use them in the mosaic
        # heading.
        lu_hist_files = fileutils.get_files_in(cons.u_HIST_DIR)

        lo_datetimes = []

        for u_hist_file in lu_hist_files:
            u_hist_file_name, u_hist_file_ext = fileutils.get_name_and_extension(u_hist_file)
            u_timestamp = u_hist_file_name.partition(' - ')[0] + u'0000'
            o_file_datetime = datetime.datetime.strptime(u_timestamp, u'%Y-%m-%d %H-%M-%S.%f')
            lo_datetimes.append(o_file_datetime)

        lo_datetimes.sort()
        o_first_file_date = lo_datetimes[0]
        o_last_date = o_datetime

        o_start = datetime.datetime(year=o_first_file_date.year,
                                    month=o_first_file_date.month,
                                    day=o_first_file_date.day)

        o_end = datetime.datetime(year=o_last_date.year,
                                  month=o_last_date.month,
                                  day=o_last_date.day,
                                  hour=23, minute=59, second=59, microsecond=999999)

    else:
        print 'ERROR: Unknown grouping period "%s"' % cons.u_PERIOD
        sys.exit()

    return o_start, o_end


def get_period_human_name(o_datetime, s_period):
    """
    Function to return the name of a period of time given the date and the period measuring system.

    :param o_datetime: Datetime object.

    :param s_period: 'daily', 'weekly', 'monthly' or 'yearly'

    :return: A string with the human name of that period. i.e. '2014, week 23'
    """

    if s_period == 'day':
        s_output = o_datetime.strftime('%d de %B de %Y')
    elif s_period == 'week':
        s_output = o_datetime.strftime('%Y, semana %U')
    elif s_period == 'month':
        s_output = o_datetime.strftime('%B de %Y').capitalize()
    elif s_period == 'year':
        s_output = o_datetime.strftime('%Y')
    elif s_period == 'all':
        s_output = 'Desde que uso #ScreenshotCollector'
    else:
        print 'ERROR: Unknown naming system "%s"' % s_period
        sys.exit()

    return s_output


def get_images(o_start_date, o_end_date, s_db_filter='', s_id_filter=''):
    """
    Function to obtain from the historic folder all the screenshots taken in certain period of time.

    :param o_start_date: Starting date. Datetime object from datetime module.

    :param o_end_date: Starting date. Datetime object from datetime module.

    :param s_db_filter: Obtain only images of games included in this database. i.e. 'snes'

    :param s_id_filter: Obtain only images of games with this id. i.e. 'a13f7640'

    :return: Nothing.
    """

    print 'Getting images in historic folder'
    print 'From: %s to %s' % (o_start_date, o_end_date)
    print '-' * 78

    i_images_to_add = 0

    for s_archived_image in fileutils.get_files_in(cons.u_HIST_DIR):
        s_src_file = os.path.join(cons.u_HIST_DIR, s_archived_image)
        s_dst_file = os.path.join(cons.u_TEMP_MOSAIC_DIR, s_archived_image)

        s_file_name, s_file_ext = fileutils.get_name_and_extension(s_archived_image)

        # The timestamp only contains two decimal values for seconds when 6 are required to convert the string to
        # a proper date object
        # TODO: move timestamp format to cons file
        # The timestamp format is the same for writing and reading so it should be a constant in the cons file. Not
        # sure if the two decimal digits for seconds is helping to maintain the file names short and "fancy" while
        # 6 decimals would make the code much simpler.
        s_file_timestamp_full = s_file_name[0:22] + 4 * '0'
        o_file_date = datetime.datetime.strptime(s_file_timestamp_full, '%Y-%m-%d %H-%M-%S.%f')

        s_file_db = s_file_name.split(' - ')[1].split(' ')[0]
        s_file_id = s_file_name.split(' - ')[1].split(' ')[1]

        if o_start_date <= o_file_date <= o_end_date:
            if s_db_filter == '' or s_db_filter == s_file_db:
                if s_id_filter == '' or s_id_filter == s_file_id:
                    i_images_to_add += 1
                    shutil.copyfile(s_src_file, s_dst_file)

                    print 'Got: %s' % s_archived_image


def get_mosaic_file_name(o_start_date, o_mid_date, o_end_date, s_period):
    """
    Function to build the file name (without extension) for the mosaic file.

    :param o_datetime:
    :param s_period:
    :return:
    """

    s_output = 'mosaic - %s - ' % s_period

    if s_period == 'day':
        s_output += '%i-%s' % (o_mid_date.year, o_mid_date.strftime('%j'))

    elif s_period == 'week':
        s_output += '%i-%s' % (o_mid_date.year, o_mid_date.strftime('%U'))

    elif s_period == 'month':
        s_output += '%i-%s' % (o_mid_date.year, o_mid_date.strftime('%m'))

    elif s_period == 'year':
        s_output += '%i' % o_mid_date.year

    elif s_period == 'all':
        s_output += '%s to %s' % (o_start_date.strftime('%Y-%m-%d'), o_end_date.strftime('%Y-%m-%d'))

    else:
        print 'ERROR: Unknown time period "%s"' % s_period
        sys.exit()

    return s_output.strip()


def process_shots():
    """
    Function that adds the title of the game to each screenshot.

    :return: Nothing
    """

    global o_game_db

    print '\nResizing images + Name stamping in temp folder'
    print '-' * 78

    # Creating every tile
    for s_image in fileutils.get_files_in(cons.u_TEMP_MOSAIC_DIR):
        s_img_full_path = os.path.join(cons.u_TEMP_MOSAIC_DIR, s_image)
        s_file_name, s_file_ext = fileutils.get_name_and_extension(s_image)

        s_db = s_file_name.split(' - ')[1].partition(' ')[0].strip()
        s_id = s_file_name.split(' - ')[1].partition(' ')[2].strip()

        if o_game_db is None or o_game_db._u_name != s_db:
            s_db_file = os.path.join(cons.s_DAT_DIR, '%s.txt' % s_db)
            o_game_db = gamecache.Database(s_db_file)

        u_title = o_game_db.get_title_by_id(s_id)

        s_commandline = 'convert "%s" ' \
                        '-background %s -resize %s -gravity center -extent %s ' \
                        '-fill %s -font "%s" -pointsize %i ' \
                        '-size %sx caption:\'%s\' -gravity Center -append ' \
                        '-gravity south -splice 0x%i ' \
                        '"%s"' \
                        % (s_img_full_path,
                           cons.u_TILE_BACKGROUND, cons.u_TILE_SIZE, cons.u_TILE_SIZE,
                           cons.u_TILE_FOOTER_COLOR, cons.s_TILE_FOOTER_FONT, cons.i_TILE_FOOTER_SIZE,
                           cons.u_TILE_SIZE.split('x')[0],
                           u_title.encode('utf8', 'strict'),
                           cons.i_TILE_BOTTOM_MARGIN,
                           s_img_full_path)

        os.system(s_commandline)

        print 'Got: %s  %s --> %s' % (s_db, s_id, u_title)


def compose_shots(u_title, s_file):
    """
    Function to
    :param u_title:
    :param s_file:
    :return:
    """

    # TODO: Modify this function to show in the heading something different when filtering by db and game id

    ls_files = fileutils.get_files_in(cons.u_TEMP_MOSAIC_DIR)
    i_files = len(ls_files)

    print '\nCreating mosaic'
    print '-' * 78
    print 'Top: %s' % u_title

    s_src_images = os.path.join(cons.u_TEMP_MOSAIC_DIR, '*.%s' % cons.u_HIST_EXT)
    s_mosaic_file = os.path.join(cons.u_HIST_MOSAIC_DIR, '%s.jpg' % s_file)

    if i_files == 0:
        print 'Img: 0 files, mosaic not created'
        s_mosaic_file = ''

    else:
        print 'Img: %i' % i_files
        s_commandline = 'montage "%s" -geometry +2+2 -tile %ix -background %s "%s"' % (s_src_images,cons.i_TILE_WIDTH,
                                                                             cons.u_TILE_BACKGROUND,
                                                                             s_mosaic_file)
        os.system(s_commandline)

        # Adding an extra title at the top of the image
        s_commandline = 'convert "%s" ' \
                        '-background %s ' \
                        '-fill %s -font "%s" -pointsize %i label:\'%s\' +swap -gravity Center -append ' \
                        '"%s"'\
                        % (s_mosaic_file,
                           cons.u_TILE_BACKGROUND,
                           cons.u_MOSAIC_HEADING_COLOR,
                           cons.s_MOSAIC_HEADING_FONT,
                           cons.i_MOSAIC_HEADING_SIZE,
                           u_title.encode('utf8', 'strict'),
                           s_mosaic_file)
        os.system(s_commandline)

        print 'Siz: %s' % fileutils.human_size(fileutils.get_size_of(s_mosaic_file))

        fileutils.clean_dir(cons.u_TEMP_MOSAIC_DIR)

    return s_mosaic_file


def demo_tweet(s_image, s_period):
    """
    This is a DEMO function used to call an external twitter library that will post the created mosaic. It won't work in
    your computer since you don't have the required path and library.

    :param s_image:
    :return:
    """

    # Importing the required twitter library
    s_current_dir = sys.path[0]
    s_twitter_lib_path = os.path.join(s_current_dir, '..', 'pgtweet')
    sys.path.append(s_twitter_lib_path)
    import pgtweet

    print '\nPosting to twitter'
    print '-' * 78

    # Creating the tweet text
    if s_period == 'day':
        ds_text = {'en': 'This is what I played yesterday #ScreenshotCollector',
                   'es': 'A ésto jugué ayer #ScreenshotCollector'}
    elif s_period == 'week':
        ds_text = {'en': 'This is what I played last week #ScreenshotCollector',
                   'es': 'A ésto jugué la semana pasada #ScreenshotCollector'}
    elif s_period == 'month':
        ds_text = {'en': 'This is what I played last month #ScreenshotCollector',
                   'es': 'A ésto jugué el mes pasado #ScreenshotCollector'}
    elif s_period == 'year':
        ds_text = {'en': 'This is what I played last year #ScreenshotCollector',
                   'es': 'A ésto jugué el año pasado #ScreenshotCollector'}
    elif s_period == 'all':
        ds_text = {'en': 'This is what I played since I started using #ScreenshotCollector',
                   'es': 'A ésto he jugado desde que estoy usando #ScreenshotCollector'}
    else:
        print 'ERROR: unknown time period "%s"' % cons.u_PERIOD
        sys.exit()

    # Sending the tweet
    # pgtweet.post(ds_text[cons.u_LANG], s_image)

    # Printing information to screen
    print 'Txt: %s' % ds_text[cons.u_LANG]
    print 'Img: %s' % s_image


def get_cmdline_options():
    """
    Function to process the commandline options.

    :return: Todo: decide.
    """

    #TODO: decide the output data of this function.

    o_arg_parser = argparse.ArgumentParser()
    o_arg_parser.add_argument('-period',
                              action='store',
                              default=cons.u_PERIOD,
                              choices=('day', 'week', 'month', 'year', 'all'),
                              required=False,
                              help='Periodicity of the mosaic. i.e. the period of time the images belong to')

    o_arg_parser.add_argument('-date',
                              action='store',
                              default=datetime.datetime.now().strftime('%Y-%m-%d'),
                              required=False,
                              help='Date in the form of YYYY-MM-DD Year, Month, Day. i.e. 2014-07-23')

    o_arg_parser.add_argument('-db',
                              action='store',
                              default='',
                              required=False,
                              help='Filter by database name. i.e. snes')

    o_arg_parser.add_argument('-id',
                              action='store',
                              default='',
                              required=False,
                              help='Filter by game id. i.e. 1e64fc82')

    args = o_arg_parser.parse_args()

    s_period = args.period
    o_datetime = datetime.datetime.strptime(args.date, '%Y-%m-%d') + datetime.timedelta(hours=12)
    s_db = args.db
    s_id = args.id

    print 'Per: %s' % s_period
    print 'Dat: %s' % args.date
    print ' DB: %s' % s_db
    print ' Id: %s' % s_id
    print

    return s_period, o_datetime, s_db, s_id

# Main program
#=======================================================================================================================

print 'Mosaic creator v0.1'
print '=' * 78

# The period type (day, week, month, year) and the datetime object are obtain from the commandline parameters. If they
# are not specified, default values are obtained from cons.py file.
s_period, o_datetime, s_db, s_id = get_cmdline_options()

# It's time to define the start and end of the time period.
o_start_date, o_end_date = get_datetime_range(o_datetime, s_period)

# Getting the files which match that timestamp using the provided pattern
get_images(o_start_date, o_end_date, s_db, s_id)

# Once the images are obtained, they can be processed using the information (full name) contained in o_game_db
o_game_db = None
process_shots()

# Time to build the required information to for a) the mosaic heading, and b) the mosaic file name
o_half_period = (o_end_date - o_start_date) / 2
o_mid_date = o_start_date + datetime.timedelta(seconds=o_half_period.total_seconds())

u_heading = get_period_human_name(o_mid_date, s_period)
u_file_name = get_mosaic_file_name(o_start_date, o_mid_date, o_end_date, s_period)

# With the required information, the mosaic can be built and saved to disk.
u_mosaic_file = compose_shots(u_heading, u_file_name)

# Example of posting the created mosaic to twitter
if u_mosaic_file != '':
    demo_tweet(u_mosaic_file, s_period)

