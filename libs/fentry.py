import os
import datetime
import fileutils


class FileEntry:
    """
    Class to archive_files information about a File Entries. A file entry is a file or a directory located in one
    source that can be a normal directory, a samba directory or a remote ftp directory.
    """
    def __init__(self):
        self.i_size = 0                     # File size (in bytes?)
        self.u_size = ''                    # File size (human readable format)

        self.f_time = None                  # File date in epoch format.
        self.u_full_name = ''               # Full file name i.e. 'picture.jpg'
        self.u_name = ''                    # Short file name i.e. 'picture'
        self.u_ext = ''                     # File extension i.e. 'jpg'
        self.u_type = 'u'                   # 'f' for file, 'd' for directory, 'u' for non-existent or unknown element
        self.u_permission = ''              # File permission string i.e. 'rwxrwxrwx'

        self.u_group = ''                   # File owner group
        self.u_user = ''                    # File owner user

        self.u_root = ''                    # Full root path of the FtpFileEntry
        self.u_full_path = ''               # Full path of the FtpFileEntry

        # Variable initialization
        self.set_size(self.i_size)

    def __str__(self):
        u_output = u'[FileEntry Object]\n'
        u_output += u'      Full Path: %s\n' % self.u_full_path
        u_output += u'           Root: %s\n' % self.u_root
        u_output += u'           Type: %s\n' % self.u_type
        u_output += u'      Full Name: %s\n' % self.u_full_name
        u_output += u'           Name: %s\n' % self.u_name
        u_output += u'      Extension: %s\n' % self.u_ext
        u_output += u'           Size: %i (%s)\n' % (self.i_size, self.u_size)
        u_output += u'    Permissions: %s\n' % self.u_permission
        u_output += u'          Group: %s\n' % self.u_group
        u_output += u'           User: %s\n' % self.u_user
        u_output += u'           Time: %s\n' % self.get_human_date()

        return u_output.encode('ascii', 'strict')

    def from_local_path(self, *s_args):
        """
        Method to build a FileEntry object from a local path.

        :param s_args:

        :return:
        """

        u_full_path = os.path.join(*s_args)

        # Building full path, file name and extension
        self.set_full_path(u_full_path)

        # Identifying file or dir
        if os.path.isfile(u_full_path):
            self.u_type = u'f'
        elif os.path.isdir(u_full_path):
            self.u_type = u'd'

        # Building date
        if self.is_file() or self.is_dir():
            self.f_time = os.path.getctime(u_full_path)

    def get_human_date(self):
        if self.f_time is not None:
            o_date = datetime.datetime.fromtimestamp(self.f_time)
            # Two decimal position should be enough for the screenshot timestamp
            s_date = o_date.strftime('%Y-%m-%d %H-%M-%S.%f')[0:-4]
            return s_date

    def is_dir(self):

        b_is_dir = False

        if self.u_type == 'd':
            b_is_dir = True

        return b_is_dir

    def is_ext(self, s_ext):
        if s_ext.lower() == self.u_ext.lower():
            b_is_ext = True
        else:
            b_is_ext = False

        return b_is_ext

    def is_file(self):

        b_is_file = False

        if self.u_type == 'f':
            b_is_file = True

        return b_is_file

    def set_name(self, s_full_name):
        self.u_full_name = s_full_name
        if s_full_name.find('.') != -1:
            self.u_name = s_full_name.rpartition('.')[0]
            self.u_ext = s_full_name.rpartition('.')[2]
        else:
            self.u_name = s_full_name
            self.u_ext = ''

    def set_size(self, i_size):
        try:
            i_size = int(i_size)
        except TypeError:
            i_size = 0

        self.i_size = i_size
        self.u_size = fileutils.human_size(self.i_size)

    def set_full_path(self, s_full_path):
        self.u_full_path = s_full_path
        self.u_root = os.path.split(s_full_path)[0]
        self.set_name(os.path.split(s_full_path)[1])

