import datetime
import os
import shutil
import sys

from libs import ftpextra
from libs import gamecache


# Configurable constants
#=======================================================================================================================
s_HOST = '192.168.0.106'
s_USER = 'xbox'
s_PASS = 'xbox'
s_ROOT = '/Hdd1/Freestyle Dash/Plugins/UserData/'
s_GROUP = 'd'  # Valid values are 'y' yearly, 'm' monthly, 'w' weekly, 'd' daily.
s_TILE_SIZE = '480x480'
s_TILE_FONT = 'media/collegia.ttf'


# Constant constants (really constant constants this time, I swear)
#=======================================================================================================================
s_TEMP_FOLDER = os.path.join('images', 'temp')
s_HISTORIC_FOLDER = os.path.join('images', 'historic')
s_MOSAIC_FOLDER = os.path.join('images', 'mosaic')


# Helper functions
#=======================================================================================================================
def get_name_and_extension(s_filename):
    if s_filename.find('.') != -1:
        s_name = s_filename.rpartition('.')[0]
        s_ext = s_filename.rpartition('.')[2]
    else:
        s_name = s_filename
        s_ext = ''

    return s_name, s_ext


def get_files_in(s_folder):
    """
    Helper function to obtain a list of files inside a folder.

    :param s_folder: The path of the folder you want to check. i.e. /user/john/desktop

    :return: A list of files.
    """
    ls_files = []

    for s_element in os.listdir(s_folder):
        s_full_path = os.path.join(s_folder, s_element)
        if os.path.isfile(s_full_path):
            ls_files.append(s_element)

    return ls_files


def clean_temp():
    """
    Helper function to clean the temp folder.

    :return: Nothing
    """
    for s_file in get_files_in(s_TEMP_FOLDER):
        s_full_path = os.path.join(s_TEMP_FOLDER, s_file)
        os.remove(s_full_path)


# Image gathering from Xbox 360
#=======================================================================================================================
def image_gathering(s_mode=''):
    """
    Function to gather all the screenshots from Xbox 360.

    :param s_mode: 'keep' to maintain the downloaded data in the console. Otherwise it will be removed.

    :return:
    """

    o_ftp = ftpextra.Ftp(s_HOST, s_USER, s_PASS)

    i_file_counter = 0

    # Getting the list of game folders in s_ROOT
    lo_game_dirs = o_ftp.list_dirs(s_ROOT)

    print 'Found screenshots for %i games' % len(lo_game_dirs)

    # For each game we download all the files included, which are '.bmp' and '.meta' files.
    for o_game_dir in lo_game_dirs:

        print '\nGame: %s' % o_game_dir.s_name
        print '--------------'

        s_game_screenshot_folder = '%s/Screenshots' % o_game_dir.s_full_path
        o_screenshot_dir = ftpextra.FtpFileEntry(o_ftp, s_game_screenshot_folder, '', s_method='from_path')

        lo_game_files = o_ftp.list_files(s_game_screenshot_folder)

        for o_game_file in lo_game_files:

            o_game_file.download('flat', s_TEMP_FOLDER)
            i_file_counter += 1

            if s_mode != 'keep':
                o_game_file.delete()

        if s_mode != 'keep':
            o_screenshot_dir.delete()
            o_game_dir.delete()

    print '%i files downloaded' % i_file_counter


# Main code - Image renaming + png conversion
#=======================================================================================================================
def image_rename():
    o_game_database = gamecache.Database()

    print 'Games in the cached database: %i' % o_game_database.get_items()

    for s_file in get_files_in(s_TEMP_FOLDER):
        s_old_file_path = os.path.join(s_TEMP_FOLDER, s_file)

        # Obtaining the file name and extension
        s_file_name, s_file_ext = get_name_and_extension(s_file)

        # Freestyle Dash takes screenshots in bmp format and it creates a .meta file with extra information. But all
        # the information included in the .meta file is already included in the .bmp so it doesn't make any sense to
        # keep that file.
        if s_file_ext != 'bmp':
            os.remove(s_old_file_path)

        if s_file_ext == 'bmp':
            s_game_id = s_file_name[0:8]
            s_raw_date_time = s_file_name[8:].ljust(20, '0')

            o_date_time = datetime.datetime.strptime(s_raw_date_time, '%Y%m%d%H%M%S%f')
            o_date = o_date_time.date()
            o_time = o_date_time.time()

            s_baked_date = o_date.strftime('%Y-%m-%d')
            s_baked_time = o_time.strftime('%H:%M:%S')
            s_title = o_game_database.get_title_by_id(s_game_id)

            s_new_filename = os.path.join(s_TEMP_FOLDER, '%s %s %s - %s' % (s_baked_date, s_baked_time, s_game_id, s_title))
            s_new_filename = s_new_filename.encode('ascii', 'ignore')
            os.rename(s_old_file_path, '%s.%s' % (s_new_filename, s_file_ext))

            s_src_image = '%s.%s' % (s_new_filename, s_file_ext)
            s_dst_image = '%s.png' % s_new_filename

            # todo: try to hide imagemagick error messages also for Windows and Mac computers
            s_commandline = 'convert "%s" -format png "%s" > /dev/null 2>&1' % (s_src_image, s_dst_image)
            os.system(s_commandline)

            os.remove(s_src_image)


# Main code - Image organization
#=======================================================================================================================
def image_organize():
    for s_element in os.listdir(s_TEMP_FOLDER):
        s_src_file = os.path.join(s_TEMP_FOLDER, s_element)
        s_dst_file = os.path.join(s_HISTORIC_FOLDER, s_element)

        if os.path.isfile(s_src_file):
            shutil.move(s_src_file, s_dst_file)


# Main code - Collage
#=======================================================================================================================
def image_mosaic():
    i_images_to_add = 0
    o_date_now = datetime.date.today()

    # Grouping name configuration to create the mosaics and to check previous states
    if s_GROUP == 'd':
        s_date_format = '%Y-%j'
        f_day_delta = 1.0
    elif s_GROUP == 'w':
        s_date_format = '%Y-%U'
        f_day_delta = 7.0
    elif s_GROUP == 'm':
        s_date_format = '%Y-%m'
        # To avoid extra complexity with 28-31 days months and leap years: 1 month = 365.25 days / 12 = 30.4375 days
        f_day_delta = 30.4375
    elif s_GROUP == 'y':
        s_date_format = '%Y'
        f_day_delta = 365.25
    else:
        print 'ERROR: Unknown grouping periodicity "%s"' % s_GROUP
        sys.exit()

    s_date_now = o_date_now.strftime(s_date_format)
    o_date_prev = o_date_now - datetime.timedelta(days=f_day_delta)
    s_date_prev = o_date_prev.strftime(s_date_format)

    # Previous mosaic creation in case it doesn't already exist
    s_prev_mosaic_file = 'mosaic_%s.jpg' % s_date_prev

    if not os.path.isfile(os.path.join(s_MOSAIC_FOLDER, s_prev_mosaic_file)):

        # Copying all the previous-period images to temp folder
        b_files_to_process = False

        ls_archived_images = get_files_in(s_HISTORIC_FOLDER)

        for s_archived_image in ls_archived_images:
            s_src_file = os.path.join(s_HISTORIC_FOLDER, s_archived_image)
            s_dst_file = os.path.join(s_TEMP_FOLDER, s_archived_image)

            s_file_name, s_file_ext = get_name_and_extension(s_archived_image)

            o_file_date = datetime.datetime.strptime(s_file_name[0:19], '%Y-%m-%d %H:%M:%S')
            s_file_date = o_file_date.strftime(s_date_format)

            if s_file_date == s_date_prev:
                i_images_to_add += 1
                shutil.copyfile(s_src_file, s_dst_file)
                b_files_to_process = True

        # Watermarking the images with the name of the game
        if b_files_to_process:
            for s_image in get_files_in(s_TEMP_FOLDER):
                s_img_full_path = os.path.join(s_TEMP_FOLDER, s_image)
                s_file_name, s_file_ext = get_name_and_extension(s_image)
                s_title = s_file_name.split('-')[3].strip()

                s_commandline = 'convert "%s" -background Black ' \
                                '-fill White -font "%s" -pointsize 36 label:\'%s\' -gravity Center -append ' \
                                '-resize %s "%s"' % (s_img_full_path, s_TILE_FONT, s_title, s_TILE_SIZE,
                                                     s_img_full_path)
                os.system(s_commandline)

            s_src_images = os.path.join(s_TEMP_FOLDER, '*.png')
            s_mosaic_file = os.path.join(s_MOSAIC_FOLDER, s_prev_mosaic_file)
            s_commandline = 'montage "%s" -geometry +2+2 -background Black "%s"' % (s_src_images, s_mosaic_file)
            os.system(s_commandline)
            print 'Mosaic: Generated mosaic with %i screenshots.' % i_images_to_add

        else:
            print 'Mosaic: No images found to be added to the mosaic.'

    else:
        print 'Mosaic: Mosaic found. NOT generating a new one. '

    clean_temp()

# Main program
#=======================================================================================================================
print '\nXbox 360 Freestyle Dash Screenshot Collector (X360 FSC)'
print '======================================================='

image_gathering('keep')
image_rename()
image_organize()
image_mosaic()
