#!/usr/local/bin/python
# -*- coding: utf8 -*-

import os
import sys

# Configuration - Basics
#=======================================================================================================================
u_TEMP_COLLECT_DIR = u'images/temp-historic'   # Directory for temporal files during collection
u_HIST_DIR = u'images/historic'                # Directory for historic images
u_HIST_EXT = u'png'                            # Historical images extension (png for quality or jpg for low size)
u_DAT_DIR = u'dats'                            # Directory containing Id/Title dat files

u_TEMP_MOSAIC_DIR = u'images/temp-mosaic'      # Directory for temporal files during mosaic creation
u_HIST_MOSAIC_DIR = u'images/mosaic'
u_LANG = u'es'                                 # Language of the program
u_FONT_DIR = u'media'                          # Directory for the fonts.

# Configuration - Mosaic creation
#=======================================================================================================================
u_PERIOD = u'week'
u_TILE_BACKGROUND = u'Black'                   # Color for the background of the mosaic (Imagemagick color).
u_TILE_FOOTER_COLOR = u'Grey'                  # Color for the title of each game in the mosaic (Imagemagick color).
u_TILE_FOOTER_FONT = u'collegia.ttf'           # Font used for the footer of each screenshot.
i_TILE_FOOTER_SIZE = 24                       # Font size used for the footer of each screenshot.
u_TILE_SIZE = u'320x180'                       # Size of each screenshot.
i_TILE_BOTTOM_MARGIN = 40                     # Margin at the bottom of the footer
i_TILE_WIDTH = 4                              # Width, in tiles, of the mosaic. i.e. 4
u_MOSAIC_HEADING_FONT = u'collegia.ttf'        # Font used for the heading of the mosaic (without full path)

i_MOSAIC_HEADING_SIZE = 32
u_MOSAIC_HEADING_COLOR = u'White'

# Constants (so they were not that constant) modification through a bit of code (don't modify anything from here)
#=======================================================================================================================
u_CWD = sys.path[0]

u_TEMP_COLLECT_DIR = os.path.join(u_CWD, u_TEMP_COLLECT_DIR)
u_HIST_DIR = os.path.join(u_CWD, u_HIST_DIR)
u_DAT_DIR = os.path.join(u_CWD, u_DAT_DIR)

u_TILE_FOOTER_FONT = os.path.join(u_CWD, u_FONT_DIR, u_TILE_FOOTER_FONT)
u_MOSAIC_HEADING_FONT = os.path.join(u_CWD, u_FONT_DIR, u_MOSAIC_HEADING_FONT)