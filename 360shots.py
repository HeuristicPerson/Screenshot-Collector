import datetime
import os

from libs import xcrapper

# Configurable constants
#=======================================================================================================================

s_HOST = '192.168.0.106'
s_USER = 'xbox'
s_PASS = 'xbox'
s_ROOT = '/Hdd1/Freestyle Dash/Plugins/UserData/'

## Constant constants (really constant constants this time, I swear)
##=======================================================================================================================
s_TEMP_FOLDER = os.path.join('images', 'temp')
s_FINAL_IMAGES_ROOT = os.path.join('images')

#
# Main code - Image gathering from Xbox 360
#=======================================================================================================================

print '\nXbox 360 Freestyle Dash Screenshot Collector (X360 FSC)'
print '======================================================='

#o_ftp = ftpextra.Ftp(s_HOST, s_USER, s_PASS)


# Getting the list of game folders in s_ROOT
#lo_game_dirs = o_ftp.list_dirs(s_ROOT)

#print 'Found screenshots for %i games' % len(lo_game_dirs)

# For each game we download all the files included, which are '.bmp' and '.meta' files.
#for o_game_dir in lo_game_dirs:

#    print '\nGame: %s' % o_game_dir.s_name
#    print '--------------'

#    s_game_screenshot_folder = '%s/Screenshots' % o_game_dir.s_full_path
#    o_screenshot_dir = ftpextra.FileEntry(o_ftp, s_game_screenshot_folder, '', s_method='from_path')

#    lo_game_files = o_ftp.list_files(s_game_screenshot_folder)

#    for o_game_file in lo_game_files:

#        o_game_file.download('flat', s_TEMP_FOLDER)
        #o_ftp.delete_file(o_game_file)
#
#    o_ftp.delete_dir(o_screenshot_dir)
#    o_ftp.delete_dir(o_game_dir)

#
# Main code - Image processing
#=======================================================================================================================
for s_element in os.listdir(s_TEMP_FOLDER):
    s_full_path = os.path.join(s_TEMP_FOLDER, s_element)

    if os.path.isfile(s_full_path):

        # Obtaining the file name and extension
        if s_element.find('.') != -1:
            s_file_name = s_element.rpartition('.')[0]
            s_file_ext = s_element.rpartition('.')[2]
        else:
            s_file_name = s_element
            s_file_ext = ''

        # Freestyle Dash takes screenshots in bmp format and it creates a .meta file with information
        if s_file_ext in ('bmp', 'meta'):
            s_game_id = s_file_name[0:8]
            s_raw_date = s_file_name[8:16]
            s_raw_time = s_file_name[16:]

            s_baked_date = datetime.datetime.strptime(s_raw_date, '%Y%m%d').date().strftime('%Y-%m-%d')
            s_baked_time = datetime.datetime.strptime(s_raw_time, '%H%M%S%f').time().strftime('%H:%M:%S')

            s_title = xcrapper.id_to_title(s_game_id)

            s_new_filename = os.path.join(s_TEMP_FOLDER, '%s %s - %s.jpg' % (s_baked_date, s_baked_time, s_title))

            if s_file_ext == 'bmp':
                s_commandline = 'convert "%s" -background Black -fill White -font collegia.ttf -pointsize 36 label:\'%s\' -gravity Center -append "%s"' % (s_full_path, s_title, s_new_filename)
                os.system(s_commandline)



