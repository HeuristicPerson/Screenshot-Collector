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
def get_datetime_range(o_datetime, s_period):
    """
    Function to build the date-stamp of the previous time section. i.e. If we were working with a weekly periodicity and
    we were in the week 30 of the year 2014, the previous timestamp would be 2014-29.

    :return: s_timestamp: A string representing a timestamp. i.e. '2014-29'.

    :return: s_date_format: A string representing the pattern for the timestamp. i.e. '%Y-%U'
    """

    #o_date_now = datetime.datetime.now()

    # Grouping name configuration to create the mosaics and to check previous states
    if s_period == 'day':
        o_yesterday = o_datetime - datetime.timedelta(days=1)
        o_start = datetime.datetime(o_yesterday.year, o_yesterday.month, o_yesterday.day, 0, 0, 0, 0)
        o_end = datetime.datetime(o_yesterday.year, o_yesterday.month, o_yesterday.day, 23, 59, 59, 999999)

    elif s_period == 'week':
        o_last_monday = o_datetime - datetime.timedelta(o_datetime.isoweekday() + 6)
        o_last_sunday = o_last_monday + datetime.timedelta(6)
        o_start = datetime.datetime(o_last_monday.year, o_last_monday.month, o_last_monday.day, 0, 0, 0, 0)
        o_end = datetime.datetime(o_last_sunday.year, o_last_sunday.month, o_last_sunday.day, 23, 59, 59, 999999)

    elif s_period == 'month':
        o_start = datetime.datetime(o_datetime.year, o_datetime.month - 1, 1, 0, 0, 0, 0)
        o_end_day = o_datetime - datetime.timedelta(days=o_datetime.day)
        o_end = datetime.datetime(o_end_day.year, o_end_day.month, o_end_day.day, 23, 59, 59, 999999)

    elif s_period == 'year':
        o_start = datetime.datetime(o_datetime.year - 1, 1, 1, 0, 0, 0, 0)
        o_end = datetime.datetime(o_datetime.year - 1, 12, 31, 23, 59, 59, 999999)

    else:
        print 'ERROR: Unknown grouping periodicity "%s"' % cons.s_PERIOD
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
    else:
        print 'ERROR: Unknown naming system "%s"' % s_period
        sys.exit()

    return s_output


def get_images(o_start_date, o_end_date):
    """
    Function to obtain from the historic folder all the screenshots taken in certain period of time.

    :param o_start_date: Starting date. Datetime object from datetime module.

    :param o_end_date: Starting date. Datetime object from datetime module.

    :return: Nothing.
    """

    print 'Getting images in historic folder'
    print 'From: %s to %s' % (o_start_date, o_end_date)
    print '-' * 78

    i_images_to_add = 0

    for s_archived_image in fileutils.get_files_in(cons.s_HIST_DIR):
        s_src_file = os.path.join(cons.s_HIST_DIR, s_archived_image)
        s_dst_file = os.path.join(cons.s_TEMP_MOSAIC_DIR, s_archived_image)

        s_file_name, s_file_ext = fileutils.get_name_and_extension(s_archived_image)

        # The timestamp only contains two decimal values for seconds when 6 are required to convert the string to
        # a proper date object
        # TODO: move timestamp format to cons file
        # The timestamp format is the same for writing and reading so it should be a constant in the cons file. Not
        # sure if the two decimal digits for seconds is helping to maintain the file names short and "fancy" while
        # 6 decimals would make the code much simpler.
        s_file_timestamp_full = s_file_name[0:22] + 4 * '0'

        o_file_date = datetime.datetime.strptime(s_file_timestamp_full, '%Y-%m-%d %H-%M-%S.%f')

        if o_start_date <= o_file_date <= o_end_date:
            i_images_to_add += 1
            shutil.copyfile(s_src_file, s_dst_file)

            print 'Got: %s' % s_archived_image


def get_mosaic_file_name(o_datetime, s_period):
    """
    Function to build the file name (without extension) for the mosaic file.

    :param o_datetime:
    :param s_period:
    :return:
    """

    s_output = 'mosaic - %s - %i ' % (cons.s_PERIOD, o_datetime.year)

    if s_period == 'day':
        s_output += 'day %s' % o_datetime.strftime('%j')

    elif s_period == 'week':
        s_output += 'week %s' % o_datetime.strftime('%U')

    elif s_period == 'month':
        s_output += 'month %s' % o_datetime.strftime('%m')

    elif s_period == 'year':
        pass

    else:
        print 'ERROR: Unknown periodicity "%s"' % cons.s_PERIOD
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
    for s_image in fileutils.get_files_in(cons.s_TEMP_MOSAIC_DIR):
        s_img_full_path = os.path.join(cons.s_TEMP_MOSAIC_DIR, s_image)
        s_file_name, s_file_ext = fileutils.get_name_and_extension(s_image)

        s_db = s_file_name.split(' - ')[1].partition(' ')[0].strip()
        s_id = s_file_name.split(' - ')[1].partition(' ')[2].strip()

        if o_game_db is None or o_game_db._s_name != s_db:
            s_db_file = os.path.join(cons.s_DAT_DIR, '%s.txt' % s_db)
            o_game_db = gamecache.Database(s_db_file)

        s_title = o_game_db.get_title_by_id(s_id)

        s_commandline = 'convert "%s" ' \
                        '-background %s -resize %s -gravity center -extent %s ' \
                        '-fill %s -font "%s" -pointsize %i -size %sx caption:\'%s\' -gravity Center -append ' \
                        ' -gravity south -splice 0x%i "%s"' \
                        % (s_img_full_path,
                           cons.s_TILE_BACKGROUND, cons.s_TILE_SIZE, cons.s_TILE_SIZE,
                           cons.s_TILE_FOOTER_COLOR, cons.s_TILE_FOOTER_FONT, cons.i_TILE_FOOTER_SIZE, cons.s_TILE_SIZE.split('x')[0], s_title,
                           cons.i_TILE_BOTTOM_MARGIN, s_img_full_path)

        os.system(s_commandline)

        print 'Got: %s  %s --> %s' % (s_db, s_id, s_title)


def compose_shots(s_title, s_file):
    """
    Function to
    :param s_title:
    :param s_file:
    :return:
    """

    ls_files = fileutils.get_files_in(cons.s_TEMP_MOSAIC_DIR)
    i_files = len(ls_files)

    print '\nCreating mosaic'
    print '-' * 78
    print 'Top: %s' % s_title

    s_src_images = os.path.join(cons.s_TEMP_MOSAIC_DIR, '*.%s' % cons.s_HIST_EXT)
    s_mosaic_file = os.path.join(cons.s_HIST_MOSAIC_DIR, '%s.jpg' % s_file)

    if i_files == 0:
        print 'Img: 0 files, mosaic not created'

    else:
        print 'Img: %i' % i_files
        s_commandline = 'montage "%s" -geometry +2+2 -tile %ix -background %s "%s"' % (s_src_images,cons.i_TILE_WIDTH,
                                                                             cons.s_TILE_BACKGROUND,
                                                                             s_mosaic_file)
        os.system(s_commandline)

        # Adding an extra title at the top of the image
        s_commandline = 'convert "%s" ' \
                        '-background %s ' \
                        '-fill %s -font "%s" -pointsize %i label:\'%s\' +swap -gravity Center -append ' \
                        '"%s"'\
                        % (s_mosaic_file,
                           cons.s_TILE_BACKGROUND,
                           cons.s_MOSAIC_HEADING_COLOR, cons.s_MOSAIC_HEADING_FONT, cons.i_MOSAIC_HEADING_SIZE, s_title,
                           s_mosaic_file)
        os.system(s_commandline)

        print 'Siz: %s' % fileutils.human_size(fileutils.get_size_of(s_mosaic_file))

        # As an example, I post the mosaic to twitter using a not included library. Create your own one or do something
        # totally different.
        # demo_tweet(s_mosaic_file)

        fileutils.clean_dir(cons.s_TEMP_MOSAIC_DIR)


def demo_tweet(s_image):
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

    # Creating the tweet text
    if cons.s_PERIOD == 'daily':
        ds_text = {'en': 'This is what I played yesterday #ScreenshotCollector',
                   'es': 'A ésto jugué ayer #ScreenshotCollector'}
    elif cons.s_PERIOD == 'weekly':
        ds_text = {'en': 'This is what I played last week #ScreenshotCollector',
                   'es': 'A ésto jugué la semana pasada #ScreenshotCollector'}
    elif cons.s_PERIOD == 'monthly':
        ds_text = {'en': 'This is what I played last month #ScreenshotCollector',
                   'es': 'A ésto jugué el mes pasado #ScreenshotCollector'}
    elif cons.s_PERIOD == 'yearly':
        ds_text = {'en': 'This is what I played last year #ScreenshotCollector',
                   'es': 'A ésto jugué el año pasado #ScreenshotCollector'}
    else:
        print 'ERROR: unknown periodicity "%s" in file cons.py' % cons.s_PERIOD
        sys.exit()

    # Sending the tweet
    pgtweet.post(ds_text[cons.s_LANG], s_image)


def get_cmdline_options():
    """
    Function to process the commandline options.

    :return: Todo: decide.
    """

    #TODO: decide the output data of this function.

    o_arg_parser = argparse.ArgumentParser()
    o_arg_parser.add_argument('-period',
                              action='store',
                              default=cons.s_PERIOD,
                              choices=('day', 'week', 'month', 'year'),
                              required=False,
                              help='Periodicity of the mosaic. i.e. the period of time the images belong to')

    o_arg_parser.add_argument('-date',
                              action='store',
                              default=datetime.datetime.now().strftime('%Y-%m-%d'),
                              required=False,
                              help='Date in the form of YYYY-MM-DD Year, Month, Day. i.e. 2014-07-23')

    args = o_arg_parser.parse_args()

    s_period = args.period
    o_datetime = datetime.datetime.strptime(args.date, '%Y-%m-%d') + datetime.timedelta(hours=12)

    #print s_period, o_datetime

    return s_period, o_datetime

# Main program
#=======================================================================================================================

# The period type (day, week, month, year) and the datetime object are obtain from the commandline parameters. If they
# are not specified, default values are obtained from cons.py file.
s_period, o_datetime = get_cmdline_options()

# It's time to define the start and end of the time period.
o_start_date, o_end_date = get_datetime_range(o_datetime, s_period)

# Getting the files which match that timestamp using the provided pattern
get_images(o_start_date, o_end_date)

# Once the images are obtained, they can be processed using the information (full name) contained in o_game_db
o_game_db = None
process_shots()

# Time to build the required information to for a) the mosaic heading, and b) the mosaic file name
o_half_period = (o_end_date - o_start_date) / 2
o_mid_date = o_start_date + datetime.timedelta(seconds=o_half_period.total_seconds())

s_heading = get_period_human_name(o_mid_date, s_period)
s_file_name = get_mosaic_file_name(o_mid_date, s_period)

# With the required information, the mosaic can be built and saved to disk.
compose_shots(s_heading, s_file_name)

