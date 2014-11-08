import os
import datetime
import files


class FileEntry:
    """
    Class to archive_files information about a File Entries. A file entry is a file or a directory located in one
    source that can be a normal directory, a samba directory or a remote ftp directory.
    """
    def __init__(self):
        #self.o_source = None                # Every file entry points to an ftp object.

        self.i_size = 0                     # File size (in bytes?)
        self.s_size = ''                    # File size (human readable format)

        self.f_time = None                  # File date (not used by now)
        self.s_full_name = ''               # Full file name i.e. 'picture.jpg'
        self.s_name = ''                    # Short file name i.e. 'picture'
        self.s_ext = ''                     # File extension i.e. 'jpg'
        self.s_type = 'u'                   # 'f' for file, 'd' for directory, 'u' for non-existent or unknown element
        self.s_permission = ''              # File permission string i.e. 'rwxrwxrwx'

        self.s_group = ''                   # File owner group
        self.s_user = ''                    # File owner user

        self.s_root = ''                    # Full root path of the FtpFileEntry
        self.s_full_path = ''               # Full path of the FtpFileEntry

        # Variable initialization
        self.set_size(self.i_size)

    def __str__(self):
        s_output = ''
        #s_output += '     Source: %s\n' % self.o_source._s_host
        s_output += '  Full Path: %s\n' % self.s_full_path
        s_output += '       Root: %s\n' % self.s_root
        s_output += '       Type: %s\n' % self.s_type
        s_output += '  Full Name: %s\n' % self.s_full_name
        s_output += '       Name: %s\n' % self.s_name
        s_output += '  Extension: %s\n' % self.s_ext
        s_output += '       Size: %i (%s)\n' % (self.i_size, self.s_size)
        s_output += 'Permissions: %s\n' % self.s_permission
        s_output += '      Group: %s\n' % self.s_group
        s_output += '       User: %s\n' % self.s_user
        s_output += '       Time: %s\n' % self.get_human_date()

        return s_output

    def from_local_path(self, *s_args):
        """
        Method to build a FileEntry object from a local path.

        :param s_args:

        :return:
        """

        s_full_path = os.path.join(*s_args)

        # Building full path, file name and extension
        self.set_full_path(s_full_path)

        # Identifying file or dir
        if os.path.isfile(s_full_path):
            self.s_type = 'f'
        elif os.path.isdir(s_full_path):
            self.s_type = 'd'

        # Building date
        if self.is_file() or self.is_dir():
            self.f_time = os.path.getctime(s_full_path)

    def get_human_date(self):
        if self.f_time is not None:
            o_date = datetime.datetime.fromtimestamp(self.f_time)
            # One decimal position should be enough for the screenshot timestamp
            s_date = o_date.strftime('%Y.%m.%d %H.%M.%S.%f')[0:-5]
            return s_date

    def is_dir(self):

        b_is_dir = False

        if self.s_type == 'd':
            b_is_dir = True

        return b_is_dir

    def is_ext(self, s_ext):
        if s_ext.lower() == self.s_ext.lower():
            b_is_ext = True
        else:
            b_is_ext = False

        return b_is_ext

    def is_file(self):

        b_is_file = False

        if self.s_type == 'f':
            b_is_file = True

        return b_is_file

    def set_name(self, s_full_name):
        self.s_full_name = s_full_name
        if s_full_name.find('.') != -1:
            self.s_name = s_full_name.rpartition('.')[0]
            self.s_ext = s_full_name.rpartition('.')[2]
        else:
            self.s_name = s_full_name
            self.s_ext = ''

    def set_size(self, i_size):
        try:
            i_size = int(i_size)
        except TypeError:
            i_size = 0

        self.i_size = i_size
        self.s_size = files.human_size(self.i_size)

    def set_full_path(self, s_full_path):
        self.s_full_path = s_full_path
        self.s_root = os.path.split(s_full_path)[0]
        self.set_name(os.path.split(s_full_path)[1])

