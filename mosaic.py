#!/usr/local/bin/python
# -*- coding: utf8 -*-

import datetime
import locale
import os
import shutil
import sys

from libs import cons
from libs import gamecache
from libs import fileutils

locale.setlocale(locale.LC_ALL, 'es_ES.utf8')


# Main code - Collage
#=======================================================================================================================
def get_period():
    """
    Function to build the date-stamp of the previous time section. i.e. If we were working with a weekly periodicity and
    we were in the week 30 of the year 2014, the previous timestamp would be 2014-29.

    :return: s_timestamp: A string representing a timestamp. i.e. '2014-29'.

    :return: s_date_format: A string representing the pattern for the timestamp. i.e. '%Y-%U'
    """

    o_date_now = datetime.datetime.now()

    # Grouping name configuration to create the mosaics and to check previous states
    if cons.s_PERIODICITY == 'daily':
        o_yesterday = o_date_now - datetime.timedelta(days=1)
        o_start = datetime.datetime(o_yesterday.year, o_yesterday.month, o_yesterday.day, 0, 0, 0, 0)
        o_end = datetime.datetime(o_yesterday.year, o_yesterday.month, o_yesterday.day, 23, 59, 59, 999999)
        #s_date_format = '%Y-%j'

    elif cons.s_PERIODICITY == 'weekly':
        o_last_monday = o_date_now - datetime.timedelta(o_date_now.isoweekday() + 6)
        o_last_sunday = o_last_monday + datetime.timedelta(6)
        o_start = datetime.datetime(o_last_monday.year, o_last_monday.month, o_last_monday.day, 0, 0, 0, 0)
        o_end = datetime.datetime(o_last_sunday.year, o_last_sunday.month, o_last_sunday.day, 23, 59, 59, 999999)
        #s_date_format = '%Y-%U'

    elif cons.s_PERIODICITY == 'monthly':
        o_start = datetime.datetime(o_date_now.year, o_date_now.month - 1, 1, 0, 0, 0, 0)
        o_end_day = o_date_now - datetime.timedelta(days=o_date_now.day)
        o_end = datetime.datetime(o_end_day.year, o_end_day.month, o_end_day.day, 23, 59, 59, 999999)
        #s_date_format = '%Y-%m'

    elif cons.s_PERIODICITY == 'yearly':
        o_start = datetime.datetime(o_date_now.year - 1, 1, 1, 0, 0, 0, 0)
        o_end = datetime.datetime(o_date_now.year - 1, 12, 31, 23, 59, 59, 999999)
        #s_date_format = '%Y'

    else:
        print 'ERROR: Unknown grouping periodicity "%s"' % cons.s_PERIODICITY
        sys.exit()

    #print 'Current timestamp: %s' % o_date_now.isoformat()
    #print 'Periodicity: %s' % cons.s_PERIODICITY
    #print 'Valid period: %s  -  %s' % (o_start.isoformat(), o_end.isoformat())

    return o_start, o_end


def get_period_human_name(o_datetime, s_naming):
    """
    Function to return the name of a period of time given the date and the period measuring system.

    :param o_datetime: Datetime object.

    :param s_naming: 'daily', 'weekly', 'monthly' or 'yearly'

    :return: A string with the human name of that period. i.e. '2014, week 23'
    """

    if s_naming == 'daily':
        s_output = o_datetime.strftime('%d de %B de %Y')
    elif s_naming == 'weekly':
        s_output = o_datetime.strftime('%Y, semana %U')
    elif s_naming == 'monthly':
        s_output = o_datetime.strftime('%B de %Y').capitalize()
    elif s_naming == 'yearly':
        s_output = o_datetime.strftime('%Y')
    else:
        print 'ERROR: Unknown naming system "%s"' % s_naming
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


def get_mosaic_file_name(o_date):

    s_output = 'mosaic - %s - %i ' % (cons.s_PERIODICITY, o_date.year)

    if cons.s_PERIODICITY == 'daily':
        s_output += 'day %s' % o_date.strftime('%j')

    elif cons.s_PERIODICITY == 'weekly':
        s_output += 'week %s' % o_date.strftime('%U')

    elif cons.s_PERIODICITY == 'monthly':
        s_output += 'month %s' % o_date.strftime('%m')

    elif cons.s_PERIODICITY == 'yearly':
        pass

    else:
        print 'ERROR: Unknown periodicity "%s"' % cons.s_PERIODICITY
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
                        '-fill %s -font "%s" -pointsize %i label:\'%s\' -gravity Center -append ' \
                        '"%s"' \
                        % (s_img_full_path,
                           cons.s_TILE_BACKGROUND, cons.s_TILE_SIZE, cons.s_TILE_SIZE,
                           cons.s_TILE_FOOTER_COLOR, cons.s_TILE_FOOTER_FONT, cons.i_TILE_FOOTER_SIZE, s_title,
                           s_img_full_path)

        os.system(s_commandline)

        print 'Got: %s  %s --> %s' % (s_db, s_id, s_title)


def compose(s_title, s_file):
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
        s_commandline = 'montage "%s" -geometry +2+2 -background %s "%s"' % (s_src_images,
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
        demo_tweet(s_mosaic_file)

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
    s_twitter_lib_path = os.path.join(s_current_dir, '..', 'pgtwitter')
    sys.path.append(s_twitter_lib_path)
    import pgtwitter

    # Creating the tweet text
    if cons.s_PERIODICITY == 'daily':
        s_text = 'This is what I played yesterday'
    elif cons.s_PERIODICITY == 'weekly':
        s_text = 'This is what I played last week'
    elif cons.s_PERIODICITY == 'monthly':
        s_text = 'This is what I played last month'
    elif cons.s_PERIODICITY == 'yearly':
        s_text = 'This is what I played last year'
    else:
        print 'ERROR: unknown periodicity "%s" in file cons.py' % cons.s_PERIODICITY
        sys.exit()

    # Sending the tweet
    pgtwitter.post(s_text, s_image)

# Main program
#=======================================================================================================================
o_game_db = None

# Obtaining the timestamp of the previous period of time and its format
o_start_date, o_end_date = get_period()

# Getting the files which match that timestamp using the provided pattern
get_images(o_start_date, o_end_date)
process_shots()

# Compose the shots into one image
o_half_period = (o_end_date - o_start_date) / 2
o_mid_date = o_start_date + datetime.timedelta(seconds=o_half_period.total_seconds())

s_heading = get_period_human_name(o_mid_date, cons.s_PERIODICITY)
s_file_name = get_mosaic_file_name(o_mid_date)

compose(s_heading, s_file_name)

