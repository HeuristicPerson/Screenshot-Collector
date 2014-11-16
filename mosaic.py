import datetime
import os
import shutil
import sys

from libs import cons
from libs import gamecache
from libs import fileutils


# Configurable constants
#=======================================================================================================================

# Tile mosaic configuration
#---------------------------------------------------------
s_TILE_FOOTER_FONT = 'media/collegia.ttf'
s_TILE_FOOTER_COLOR = 'White'
s_TILE_HEADING_FONT = 'media/collegia.ttf'
s_TILE_HEADING_COLOR = 'White'


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
        o_start_date = datetime.datetime(o_yesterday.year, o_yesterday.month, o_yesterday.day, 0, 0, 0, 0)
        o_end_date = datetime.datetime(o_yesterday.year, o_yesterday.month, o_yesterday.day, 23, 59, 59, 999999)
        #s_date_format = '%Y-%j'

    elif cons.s_PERIODICITY == 'weekly':
        o_last_monday = o_date_now - datetime.timedelta(o_date_now.isoweekday() + 6)
        o_last_sunday = o_last_monday + datetime.timedelta(6)
        o_start_date = datetime.datetime(o_last_monday.year, o_last_monday.month, o_last_monday.day, 0, 0, 0, 0)
        o_end_date = datetime.datetime(o_last_sunday.year, o_last_sunday.month, o_last_sunday.day, 23, 59, 59, 999999)
        #s_date_format = '%Y-%U'

    elif cons.s_PERIODICITY == 'monthly':
        o_start_date = datetime.datetime(o_date_now.year, o_date_now.month - 1, 1, 0, 0, 0, 0)
        o_end_day = o_date_now - datetime.timedelta(days=o_date_now.day)
        o_end_date = datetime.datetime(o_end_day.year, o_end_day.month, o_end_day.day, 23, 59, 59, 999999)
        #s_date_format = '%Y-%m'

    elif cons.s_PERIODICITY == 'yearly':
        o_start_date = datetime.datetime(o_date_now.year - 1, 1, 1, 0, 0, 0, 0)
        o_end_date = datetime.datetime(o_date_now.year - 1, 12, 31, 23, 59, 59, 999999)
        #s_date_format = '%Y'

    else:
        print 'ERROR: Unknown grouping periodicity "%s"' % cons.s_PERIODICITY
        sys.exit()

    print 'Current timestamp: %s' % o_date_now.isoformat()
    print 'Periodicity: %s' % cons.s_PERIODICITY
    print 'Valid period: %s  -  %s' % (o_start_date.isoformat(), o_end_date.isoformat())

    return o_start_date, o_end_date


def get_images(s_valid_timestamp, s_date_format):
#    global s_date_prev
#    global s_mosaic_name

    print 'Getting images from historic folder'
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
        s_file_timestamp_short = o_file_date.strftime(s_date_format)

        if s_file_timestamp_short == s_valid_timestamp:
            i_images_to_add += 1
            shutil.copyfile(s_src_file, s_dst_file)

            print 'Got: %s  %s' % (s_file_timestamp_short, s_file_name)


def watermarking():
    """
    Function that adds the title of the game to each screenshot.

    :return: Nothing
    """

    global o_game_db

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


def composition():
    s_src_images = os.path.join(cons.s_TEMP_MOSAIC_DIR, '*.%s' % cons.s_HIST_EXT)
    s_mosaic_file = os.path.join(cons.s_HIST_MOSAIC_DIR, '%s.jpg' % s_mosaic_name)

    s_commandline = 'montage "%s" -geometry +2+2 -background %s "%s"' % (s_src_images, cons.s_TILE_BACKGROUND, s_mosaic_file)
    os.system(s_commandline)
#
#            # Adding an extra title at the top of the image
#            s_commandline = 'convert "%s" ' \
#                            '-background %s ' \
#                            '-fill %s -font "%s" -pointsize %i label:\'%s\' +swap -gravity Center -append ' \
#                            '"%s"'\
#                            % (s_mosaic_file,
#                               s_TILE_BACKGROUND,
#                               s_TILE_HEADING_COLOR, s_TILE_HEADING_FONT, i_TILE_HEADING_SIZE, s_heading,
#                               s_mosaic_file)
#            os.system(s_commandline)
#
#            print 'Mosaic: Generated mosaic with %i screenshots.' % i_images_to_add
#
#        else:
#            print 'Mosaic: No images found to be added to the mosaic.'
#
#    else:
#        print 'Mosaic: Mosaic found. NOT generating a new one. '
#
#    clean_temp()
#

# Main program
#=======================================================================================================================
o_game_db = None
s_mosaic_pattern = ''

# Obtaining the timestamp of the previous period of time and its format
o_start_date, o_end_date = get_period()

# Getting the files which match that timestamp using the provided pattern
#get_images(s_date_prev, s_date_format)


#print s_date_prev, s_date_format

#get_required_images()
#
#print '\nProcessing individual images'
#print '-' * 78
#
#watermarking()
#composition()
