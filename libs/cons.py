import os
import sys

# Configuration - Basics
#=======================================================================================================================
s_TEMP_DIR = 'images/temp'              # Directory for temporal files
s_HIST_DIR = 'images/historic'          # Directory for historic images
s_HIST_EXT = 'png'                      # Historical images extension (typically png for quality or jpg for low size)
s_DAT_DIR = 'dats'                      # Directory containing Id/Title dat files

# Adding full path to relative paths
s_CWD = sys.path[0]

s_TEMP_DIR = os.path.join(s_CWD, s_TEMP_DIR)
s_HIST_DIR = os.path.join(s_CWD, s_HIST_DIR)
s_DAT_DIR = os.path.join(s_CWD, s_DAT_DIR)
