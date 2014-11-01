import os

from libs import ftpextra
from libs import gamecache
from libs import shotname

# Configuration - Basics
#=======================================================================================================================
s_TEMP_DIR = 'images/temp'              # Directory for temporal files
s_HIST_DIR = 'images/historic'          # Directory for historic images
s_HIST_EXT = 'png'                      # Historical images extension (typically png for quality or jpg for low size)
s_DAT_DIR = 'dats'                      # Directory containing Id/Title dat files


# Configuration - FTPs
#=======================================================================================================================
lo_ftp_configs = []

# Xbox 360 FTP configuration
o_ftp_cfg_xbox360 = ftpextra.FtpCfg()
o_ftp_cfg_xbox360.s_name = 'xbox360'                                    # Name of this cfg (used for DB and renaming)
o_ftp_cfg_xbox360.s_host = '192.168.0.106'                              # Address of the FTP
o_ftp_cfg_xbox360.s_user = 'xbox'                                       # User for the FTP
o_ftp_cfg_xbox360.s_pass = 'xbox'                                       # Password for the FTP
o_ftp_cfg_xbox360.s_root = '/Hdd1/Freestyle Dash/Plugins/UserData'      # Folder where to search for images
o_ftp_cfg_xbox360.ls_get_extensions = ('bmp')                           # Use only lowercase extensions
o_ftp_cfg_xbox360.ls_del_extensions = ('bmp', 'meta')                   # Use only lowercase extensions
o_ftp_cfg_xbox360.b_recursive = True                                    # Searching for images recursively
o_ftp_cfg_xbox360.b_dir_keep = False                                    # Image folders are deleted (if empty)

lo_ftp_configs.append(o_ftp_cfg_xbox360)

# Configuration - Standard folders (I assume this will also work with samba folders)
#=======================================================================================================================


# Helper functions
#=======================================================================================================================
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


def get_name_and_extension(s_filename):
    """
    Helper function to obtain the file name and file extension from a full filename.file_extension string.

    :param s_filename: The full file name. i.e. 'my picture.jpg'

    :return: A tuple with two values, filename and file_extension. i.e. 'my picture' and 'jpg'
    """

    if s_filename.find('.') != -1:
        s_name = s_filename.rpartition('.')[0]
        s_ext = s_filename.rpartition('.')[2]
    else:
        s_name = s_filename
        s_ext = ''

    return s_name, s_ext


# Step function - FTP image gathering
#=======================================================================================================================
def ftp_gather(o_ftp_config):
    """
    Helper function to download images from a ftp server being given the o_ftp_cfg object.

    :param o_ftp_config: FTP configuration which has no just ftp config but also which kind of files to download, which
                         ones to avoid, etc...

    :return: Nothing
    """

    o_ftp = ftpextra.Ftp(o_ftp_config)
    if o_ftp.b_connected:
        print 'FTP: %s (%s) connected' % (o_ftp_config.s_name, o_ftp.s_host)
        print '-----------------'
        o_ftp_elements = o_ftp.list_elements(o_ftp_config.s_root, b_recursive=True)

        # After obtaining all the elements, the list needs to be reversed because, if we want to delete the elements,
        # first we must delete the childs and after the parents. Since the list of elements is built in the natural way
        # (first parents, then childs, then grandchilds), it must be reversed.
        o_ftp_elements = reversed(o_ftp_elements)

        for o_ftp_element in o_ftp_elements:
            if o_ftp_element.s_type == 'f':
                if o_ftp_element.s_ext.lower() in o_ftp_config.ls_get_extensions:
                    print 'Downloading file: %s  %s' % (o_ftp_element.s_full_name, o_ftp_element.s_size)
                    o_ftp_element.download('flat', s_TEMP_DIR)

                if o_ftp_element.s_ext.lower() in o_ftp_config.ls_del_extensions:
                    print '   Deleting file: %s  %s' % (o_ftp_element.s_full_name, o_ftp_element.s_size)
                    o_ftp_element.delete()

            elif o_ftp_element.s_type == 'd' and not o_ftp_config.b_dir_keep:
                o_ftp_element.delete()

    else:
        print 'FTP: %s (%s) NOT connected' % (o_ftp_config.s_name, o_ftp.s_host)
        print '---------------------'


# Step function - Image renaming and storing in the historical folder
#=======================================================================================================================
def img_store(o_ftp_config):
    """
    Function to move the images obtained from one screenshot source, rename them using the standard format (date time -
    system id - name.png) and store them in the historic folder.

    :param o_ftp_config:

    :return: Nothing
    """

    o_games_db = gamecache.Database(o_ftp_config.s_name, os.path.join(s_DAT_DIR, '%s.txt' % o_ftp_config.s_name))

    ls_orig_files = get_files_in(s_TEMP_DIR)

    for s_orig_file in ls_orig_files:

        s_file_name, s_file_ext = get_name_and_extension(s_orig_file)

        s_hist_name = shotname.raw_to_historic(s_file_name, o_games_db)

        s_orig_file_path = os.path.join(s_TEMP_DIR, s_orig_file)
        # s_conv_file_path = os.path.join(s_TEMP_DIR, '%s.%s' % (s_hist_name, s_HIST_EXT))
        s_dest_file_path = os.path.join(s_HIST_DIR, '%s.%s' % (s_hist_name, s_HIST_EXT))

        s_cmd = 'convert "%s" "%s"' % (s_orig_file_path, s_dest_file_path)
        os.system(s_cmd)



# Main code
#=======================================================================================================================
print 'Screenshot gatherer v0.1'
print '========================'

for o_ftp_config in lo_ftp_configs:
    #ftp_gather(o_ftp_config)
    img_store(o_ftp_config)