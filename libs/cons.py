import os
import sys

# Configuration - Basics
#=======================================================================================================================
s_TEMP_COLLECT_DIR = 'images/temp-collect'  # Directory for temporal files during collection
s_HIST_DIR = 'images/historic'              # Directory for historic images
s_HIST_EXT = 'png'                          # Historical images extension (png for quality or jpg for low size)
s_DAT_DIR = 'dats'                          # Directory containing Id/Title dat files

s_TEMP_MOSAIC_DIR = 'images/temp-mosaic'    # Directory for temporal files during mosaic creation
s_HIST_MOSAIC_DIR = 'images/mosaic'
s_LANG = 'es'
s_FONT_DIR = 'media'                        # Directory for the fonts.

# Configuration - Mosaic creation
#=======================================================================================================================
s_PERIODICITY = 'weekly'
s_TILE_BACKGROUND = 'Black'          # Color for the background of the mosaic (Imagemagick color).
s_TILE_FOOTER_COLOR = 'Grey'         # Color for the title of each game in the mosaic (Imagemagick color).
s_TILE_FOOTER_FONT = 'collegia.ttf'  # Font used for the footer of each screenshot.
i_TILE_FOOTER_SIZE = 24              # Font size used for the footer of each screenshot.
s_TILE_SIZE = '320x180'              # Size of each screenshot.
s_MOSAIC_HEADING_FONT = 'media/collegia.ttf'

i_MOSAIC_HEADING_SIZE = 32
s_MOSAIC_HEADING_COLOR = 'White'

# Adding full path to relative paths
s_CWD = sys.path[0]

s_TEMP_COLLECT_DIR = os.path.join(s_CWD, s_TEMP_COLLECT_DIR)
s_HIST_DIR = os.path.join(s_CWD, s_HIST_DIR)
s_DAT_DIR = os.path.join(s_CWD, s_DAT_DIR)

s_TILE_FOOTER_FONT = os.path.join(s_CWD, s_FONT_DIR, s_TILE_FOOTER_FONT)