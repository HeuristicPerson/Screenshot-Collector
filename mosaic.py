import datetime
import os
import shutil
import sys

from libs import gamecache


# Configurable constants
#=======================================================================================================================

# Tile mosaic configuration
#---------------------------------------------------------
s_TILE_GROUP = 'd'  # Valid values are 'y' yearly, 'm' monthly, 'w' weekly, 'd' daily.
s_TILE_BACKGROUND = 'Black'
s_TILE_SIZE = '480x480'
s_TILE_FOOTER_FONT = 'media/collegia.ttf'
s_TILE_FOOTER_COLOR = 'White'
s_TILE_HEADING_FONT = 'media/collegia.ttf'
s_TILE_HEADING_COLOR = 'White'
i_TILE_FOOTER_SIZE = 64
i_TILE_HEADING_SIZE = 128


# Main code - Collage
#=======================================================================================================================
def image_mosaic():
    i_images_to_add = 0
    o_date_now = datetime.date.today()

    # Grouping name configuration to create the mosaics and to check previous states
    if s_TILE_GROUP == 'd':
        s_date_format = '%Y-%j'
        f_day_delta = 1.0
        s_heading_tpl = '%d-%m-%Y'
    elif s_TILE_GROUP == 'w':
        s_date_format = '%Y-%U'
        f_day_delta = 7.0
        s_heading_tpl = 'Semana %U de %Y'
    elif s_TILE_GROUP == 'm':
        s_date_format = '%Y-%m'
        # To avoid extra complexity with 28-31 days months and leap years: 1 month = 365.25 days / 12 = 30.4375 days
        f_day_delta = 30.4375
        s_heading_tpl = '%B de %Y'
    elif s_TILE_GROUP == 'y':
        s_date_format = '%Y'
        f_day_delta = 365.25
        s_heading_tpl = '%Y'
    else:
        print 'ERROR: Unknown grouping periodicity "%s"' % s_TILE_GROUP
        sys.exit()

    o_date_prev = o_date_now - datetime.timedelta(days=f_day_delta)
    s_date_prev = o_date_prev.strftime(s_date_format)

    s_heading = o_date_prev.strftime(s_heading_tpl)

    # Previous mosaic creation in case it doesn't already exist
    s_prev_mosaic_file = 'mosaic_%s.jpg' % s_date_prev

    if not os.path.isfile(os.path.join(s_MOSAIC_FOLDER, s_prev_mosaic_file)):

        # Copying all the previous-period images to temp folder
        b_files_to_process = False

        for s_archived_image in get_files_in(s_HISTORIC_FOLDER):
            s_src_file = os.path.join(s_HISTORIC_FOLDER, s_archived_image)
            s_dst_file = os.path.join(s_TEMP_FOLDER, s_archived_image)

            s_file_name, s_file_ext = get_name_and_extension(s_archived_image)

            o_file_date = datetime.datetime.strptime(s_file_name[0:19], '%s %s' % (s_DATE_PATTERN, s_TIME_PATTERN))
            s_file_date = o_file_date.strftime(s_date_format)

            if s_file_date == s_date_prev:
                i_images_to_add += 1
                shutil.copyfile(s_src_file, s_dst_file)
                b_files_to_process = True

        # Watermarking the images with the name of the game
        if b_files_to_process:
            # Creating every tile
            for s_image in get_files_in(s_TEMP_FOLDER):
                s_img_full_path = os.path.join(s_TEMP_FOLDER, s_image)
                s_file_name, s_file_ext = get_name_and_extension(s_image)
                s_title = o_game_database.get_title_by_id(s_file_name[20:28])

                s_commandline = 'convert "%s" -background %s ' \
                                '-fill %s -font "%s" -pointsize %i label:\'%s\' -gravity Center -append ' \
                                '-resize %s "%s"'\
                                % (s_img_full_path, s_TILE_BACKGROUND,
                                   s_TILE_FOOTER_COLOR, s_TILE_FOOTER_FONT, i_TILE_FOOTER_SIZE, s_title,
                                   s_TILE_SIZE, s_img_full_path)
                os.system(s_commandline)

            # Composing the tiles
            s_src_images = os.path.join(s_TEMP_FOLDER, '*.%s' % s_STORE_EXT)
            s_mosaic_file = os.path.join(s_MOSAIC_FOLDER, s_prev_mosaic_file)

            s_commandline = 'montage "%s" -geometry +2+2 -background %s "%s"' % (s_src_images, s_TILE_BACKGROUND, s_mosaic_file)
            os.system(s_commandline)

            # Adding an extra title at the top of the image
            s_commandline = 'convert "%s" ' \
                            '-background %s ' \
                            '-fill %s -font "%s" -pointsize %i label:\'%s\' +swap -gravity Center -append ' \
                            '"%s"'\
                            % (s_mosaic_file,
                               s_TILE_BACKGROUND,
                               s_TILE_HEADING_COLOR, s_TILE_HEADING_FONT, i_TILE_HEADING_SIZE, s_heading,
                               s_mosaic_file)
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

o_game_database = gamecache.Database(s_CACHE_FILE)

image_gathering('keep')
image_rename()
image_organize()
image_mosaic()
