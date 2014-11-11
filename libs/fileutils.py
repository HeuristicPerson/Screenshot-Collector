"""
Helper functions for file handling
"""
import os

def clean_dir(s_dir):
    """
    Helper function to clean the temporary directory.

    :return: Nothing.
    """

    if os.path.isdir(s_dir):
        ls_files = get_files_in(s_dir)

        for s_file in ls_files:
            s_full_path = os.path.join(s_dir, s_file)
            os.remove(s_full_path)


def get_files_in(s_dir):
    """
    Helper function to obtain a list of files inside a folder.

    :param s_dir: The path of the folder you want to check. i.e. /user/john/desktop

    :return: A list of files.
    """
    ls_files = []

    if os.path.isdir(s_dir):
        for s_element in os.listdir(s_dir):
            s_full_path = os.path.join(s_dir, s_element)
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


def get_size_of(s_filename):
    if os.path.isfile(s_filename):
        return os.path.getsize(s_filename)


def human_size(i_size):
    """
    Helper function to generate 'human readable' file sizes from raw number of bytes size.

    :return: A string indicating the size with one decimal value and the proper units. i.e. '1.2 KB'
    """

    s_output = ''

    for s_unit in ('bytes', 'KB', 'MB', 'GB'):

        if -1024.0 < i_size < 1024.0:
            if s_unit != 'bytes':
                s_output = '%3.1f %s' % (i_size, s_unit)
            else:
                s_output = '%3.0f %s' % (i_size, s_unit)

            break

        i_size /= 1024.0

    if s_output == '':
        s_output = '%3.1f %s' % (i_size, 'TB')

    return s_output.strip()