#!/usr/local/bin/python
# -*- coding: utf8 -*-

import os
import sys

# Configuration - Basics
#=======================================================================================================================
u_CWD = sys.path[0]                                           # Directory of the launching script (dir of collector.py
                                                              # and mosaic.py)
u_DAT_DIR = os.path.join(u_CWD, u'dats')                      # Dats folder
u_FONT_DIR = os.path.join(u_CWD, u'media')                    # Directory for the fonts

# Configuration - Mosaic creation
#=======================================================================================================================
#u_PERIOD = u'week'
#u_TILE_BACKGROUND = u'Black'                   # Color for the background of the mosaic (Imagemagick color).
#u_TILE_FOOTER_COLOR = u'Grey'                  # Color for the title of each game in the mosaic (Imagemagick color).
#u_TILE_FOOTER_FONT = u'collegia.ttf'           # Font used for the footer of each screenshot.
#i_TILE_FOOTER_SIZE = 24                       # Font size used for the footer of each screenshot.
#u_TILE_SIZE = u'320x180'                       # Size of each screenshot.
#i_TILE_BOTTOM_MARGIN = 40                     # Margin at the bottom of the footer
#i_TILE_WIDTH = 4                              # Width, in tiles, of the mosaic. i.e. 4
#u_MOSAIC_HEADING_FONT = u'collegia.ttf'        # Font used for the heading of the mosaic (without full path)

#i_MOSAIC_HEADING_SIZE = 32
#u_MOSAIC_HEADING_COLOR = u'White'

