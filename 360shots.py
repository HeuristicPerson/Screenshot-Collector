import datetime
import os
import shutil

from libs import ftpextra
from libs import gamecache


# Configurable constants
#=======================================================================================================================

s_HOST = '192.168.0.106'
s_USER = 'xbox'
s_PASS = 'xbox'
s_ROOT = '/Hdd1/Freestyle Dash/Plugins/UserData/'
s_GROUP = 'month'


# Constant constants (really constant constants this time, I swear)
#=======================================================================================================================

s_TEMP_FOLDER = os.path.join('images', 'temp')
s_HISTORIC_FOLDER = os.path.join('images', 'historic')


#
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


# Image gathering from Xbox 360
#=======================================================================================================================
def image_gathering():

    o_ftp = ftpextra.Ftp(s_HOST, s_USER, s_PASS)


    # Getting the list of game folders in s_ROOT
    lo_game_dirs = o_ftp.list_dirs(s_ROOT)

    print 'Found screenshots for %i games' % len(lo_game_dirs)

    # For each game we download all the files included, which are '.bmp' and '.meta' files.
    for o_game_dir in lo_game_dirs:

        print '\nGame: %s' % o_game_dir.s_name
        print '--------------'

        s_game_screenshot_folder = '%s/Screenshots' % o_game_dir.s_full_path
        o_screenshot_dir = ftpextra.FileEntry(o_ftp, s_game_screenshot_folder, '', s_method='from_path')

        lo_game_files = o_ftp.list_files(s_game_screenshot_folder)

        for o_game_file in lo_game_files:

            o_game_file.download('flat', s_TEMP_FOLDER)
            #o_ftp.delete_file(o_game_file)
#
#           o_ftp.delete_dir(o_screenshot_dir)
#           o_ftp.delete_dir(o_game_dir)


# Image processing + Organization
#=======================================================================================================================
def image_processing():
    o_Game_Database = gamecache.Database()

    print 'Games in the cached database: %i' % o_Game_Database.get_items()

    for s_element in os.listdir(s_TEMP_FOLDER):
        s_old_file_path = os.path.join(s_TEMP_FOLDER, s_element)

        if os.path.isfile(s_old_file_path):

            # Obtaining the file name and extension
            s_file_name, s_file_ext = get_name_and_extension(s_element)

            # Freestyle Dash takes screenshots in bmp format and it creates a .meta file with extra information.
            if s_file_ext in ('bmp', 'meta'):
                s_game_id = s_file_name[0:8]
                s_raw_date_time = s_file_name[8:].ljust(20, '0')

                o_date_time = datetime.datetime.strptime(s_raw_date_time, '%Y%m%d%H%M%S%f')
                o_date = o_date_time.date()
                o_time = o_date_time.time()

                s_baked_date = o_date.strftime('%Y-%m-%d')
                s_baked_time = o_time.strftime('%H:%M:%S')

                s_title = o_Game_Database.get_title_by_id(s_game_id)

                s_new_filename = os.path.join(s_TEMP_FOLDER, '%s %s - %s' % (s_baked_date, s_baked_time, s_title))

#                print '%s --> %s' % (s_old_file_path, '%s.%s' % (s_new_filename, s_file_ext))

                os.rename(s_old_file_path, '%s.%s' % (s_new_filename, s_file_ext))

                if s_file_ext == 'bmp':
                    s_src_image = '%s.%s' % (s_new_filename, s_file_ext)
                    s_dst_image = '%s.png' % s_new_filename

                    s_commandline = 'convert "%s" -format png "%s"' % (s_src_image, s_dst_image)

                    print s_commandline
                    os.system(s_commandline)
                    os.remove(s_src_image)


# Main code - Image organization
#=======================================================================================================================
def image_organize():
    for s_element in os.listdir(s_TEMP_FOLDER):
        s_src_file = os.path.join(s_TEMP_FOLDER, s_element)
        s_dst_file = os.path.join(s_HISTORIC_FOLDER, s_element)

        if os.path.isfile(s_src_file):

            # Moving the files to the historic folder
            print 'src --> %s' % s_src_file
            print 'dst --> %s' % s_dst_file

            shutil.move(s_src_file, s_dst_file)


# Main program
#=======================================================================================================================
print '\nXbox 360 Freestyle Dash Screenshot Collector (X360 FSC)'
print '======================================================='

#image_gathering()
image_processing()
#image_organize()
