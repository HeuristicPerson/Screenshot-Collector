import ftplib
import os
import shutil
import sys

import cons
import fentry
import files
import gamecache
import shotname


class ShotSource():
    """
    Class to archive_files information about a source (ftp, folder, samba folder... maybe more in the future) where screenshots
    can be found.
    """

    def __init__(self, s_name):
        self.s_name = s_name               # Name of the source

        self._s_dat_file = ''              # Name of the dat file
        self._s_src_scheme = ''            # Source naming scheme (emulators have different screenshot naming schemes)

        self._s_type = ''                  # Type of source ('dir', 'ftp', 'smb' by now)
        self._s_host = ''                  # Host. i.e. '192.168.0.100'
        self._s_root = ''                  # Root folder of the FTP where screenshots are located. i.e. '/data/'

        self._s_user = ''                  # The name of the user of the FTP. i.e. 'john'
        self._s_pass = ''                  # The password for the user. i.e. '123456'

        self._i_timeout = 5                # Timeout

        self._ls_get_exts = ('')           # File exts to download_file (case insensitive). i.e. ('jpg', 'png')
        self._ls_del_exts = ('')           # File exts to delete (case insensitive). i.e. ('bak', 'txt')

        self._b_recursive = True           # Should search in sub-folders inside the root folder?
        self._b_dir_keep = True            # Should the empty folders be kept in the FTP?
        self.o_source = None               # The real source behind the MetaObject
        self.b_connected = False           # Is the source connected?

        self.s_hist_ext = cons.s_HIST_EXT  # Extension for the archived screenshots

    def __str__(self):
        s_output = '%s, %s source at %s' % (self.s_name, self._s_type, self._s_host)
        return s_output

    def _list_file_entries(self):
        """
        Method to list all the elements present in the source.
        :return:
        """

        lo_file_entries = []

        if self.b_connected:

            if self._s_type == 'dir':
                lo_file_entries = self.o_source.list_file_entries(self._s_root, b_recursive=self._b_recursive)

            elif self._s_type == 'ftp':
                lo_file_entries = self.o_source.list_file_entries(self._s_root, b_recursive=self._b_recursive)

            elif self._s_type == 'samba':
                pass

        # Since the list of elements could be used to delete everything, it's needed that it's reversed to list first
        # the childs and then the parents. This way you will delete first the childs and then the parents. The opposite
        # order would lead you to a situation where you would be trying to delete a folder while it stills had the
        # content inside.
        return reversed(lo_file_entries)

    def _connect(self):
        if self._s_type == 'dir':
            # todo: add support for folders
            self.o_source = Dir(self._s_root)
            self.b_connected = True

        elif self._s_type == 'ftp':
            self.o_source = Ftp(self._s_host, self._s_user, self._s_pass, 5)
            self.b_connected = True

        elif self._s_type == 'samba':
            # todo: add support for samba remote folders
            pass

    def _disconnect(self):
        """
        Method to _disconnect the source.

        :return: Nothing.
        """

        self.o_source = None
        self.b_connected = False

    def download_files(self, s_dst_dir):
        """
        Method to download_file all the screenshots from a source.

        :param s_dst_dir: Destination for the images. i.e. '/home/john/temp-images'

        :return: Nothing
        """

        print 'Gathering images from source: %s (%s, %s)' % (self.s_name, self._s_type, self._s_host)
        print 'Downloading images from: %s (%s)' % (self.s_name, self._s_host)
        print '------------------------------------------------------'

        self._connect()

        lo_remote_fentries = self._list_file_entries()

        # Workaround to get the database name using a file entry object instead of directly parse the database file
        # path.
        o_db_fentry = fentry.FileEntry()
        o_db_fentry.from_local_path(self._s_dat_file)
        s_db_name = o_db_fentry.s_name

        i_files_downloaded = 0
        i_bytes_downloaded = 0
        i_files_deleted = 0
        i_bytes_deleted = 0
        i_dirs_deleted = 0

        for o_remote_fentry in lo_remote_fentries:

            # Downloading of files with selected extensions
            if o_remote_fentry.is_file() and o_remote_fentry.s_ext in self._ls_get_exts:

                # Adding extra information (timestamp, database name, and source naming scheme) seems to be a good idea
                # to be safe. i.e. something fails and you end with a lot of mixed files from many different sources in
                # your temp folder
                s_dst_name = '%s - %s %s - %s' % (o_remote_fentry.get_human_date(),
                                                  s_db_name, self._s_src_scheme,
                                                  o_remote_fentry.s_full_name)

                self.o_source.download_file(o_remote_fentry, s_dst_dir, s_dst_name)

                i_files_downloaded += 1
                i_bytes_downloaded += o_remote_fentry.i_size
                print 'Downloaded: %s  %s' % (o_remote_fentry.s_full_name, o_remote_fentry.s_size)

            # Deletion of files with selected extensions
            if o_remote_fentry.is_file() and o_remote_fentry.s_ext.lower() in self._ls_del_exts:
                print '   Deleted: %s  %s' % (o_remote_fentry.s_full_name, o_remote_fentry.s_size)
                self.o_source.delete(o_remote_fentry)
                i_files_deleted += 1
                i_bytes_deleted += o_remote_fentry.i_size

            # Removal of empty folders
            if o_remote_fentry.is_dir() and not self._b_dir_keep:
                if self.o_source.delete(o_remote_fentry):
                    i_dirs_deleted += 1

        print '            Files downloaded: %i (%s)' % (i_files_downloaded, files.human_size(i_bytes_downloaded))
        print '               Files deleted: %i (%s)' % (i_files_deleted, files.human_size(i_bytes_deleted))
        print '                Dirs deleted: %i' % i_dirs_deleted
        print

        self._disconnect()

    def archive_files(self, s_src_dir, s_dst_dir):
        """
        Method to rename, convert and archive_files the images found in s_src_dir, to s_dst_dir

        :param s_src_dir: Source directory. i.e. '/home/john/temp'

        :param s_dst_dir: Destination directory. i.e. '/home/john/screenshot-archive_files'

        :return: Nothing
        """

        print 'Archiving images from: %s (%s)' % (self.s_name, self._s_host)
        print '------------------------------------------------------'

        o_games_db = gamecache.Database(self.s_name, self._s_dat_file)

        i_files_processed = 0
        i_orig_size = 0
        i_mod_size = 0

        for s_src_file in files.get_files_in(s_src_dir):
            s_orig_name, s_orig_ext = files.get_name_and_extension(s_src_file)

            s_arch_name = shotname.raw_to_historic(self._s_src_scheme, o_games_db, s_orig_name)

            s_dst_file = '%s.%s' % (s_arch_name, self.s_hist_ext)

            s_src_img = os.path.join(s_src_dir, s_src_file)
            s_dst_img = os.path.join(s_dst_dir, s_dst_file)

            s_cmd = 'convert "%s" "%s" 2>/dev/null' % (s_src_img, s_dst_img)
            os.system(s_cmd)

            print '      From: %s  %s' % (s_src_file, files.human_size(files.get_size_of(s_src_img)))
            print '        To: %s  %s' % (s_dst_file, files.human_size(files.get_size_of(s_dst_img)))

            i_files_processed += 1
            i_orig_size += files.get_size_of(s_src_img)
            i_mod_size += files.get_size_of(s_dst_img)

            os.remove(s_src_img)

        print '            Files converted: %i' % i_files_processed
        print '              Original size: %s' % files.human_size(i_orig_size)
        if i_orig_size != 0:
            print '              Archived size: %s (%0.1f%%)' % (files.human_size(i_mod_size),
                                                                 100.0*i_mod_size/i_orig_size)
        else:
            print '              Archived size: %s (%0.1f%%)' % (files.human_size(i_mod_size), 0.0)
        print

    def set_clean_dirs(self):
        self._b_dir_keep = False

    def set_db_and_scheme(self, s_db, s_scheme):
        s_full_db_path = os.path.join(cons.s_DAT_DIR, '%s.txt' % s_db)
        self._s_dat_file = s_full_db_path

        self._s_src_scheme = s_scheme

    def set_del_exts(self, *s_exts):

        ls_del_exts = []

        for s_ext in s_exts:
            s_ext = s_ext.lower()
            ls_del_exts.append(s_ext)

        self._ls_del_exts = tuple(ls_del_exts)

    def set_get_exts(self, *s_exts):
        """
        Method to define the extensions to download/get from the source.

        :param: s_exts: List of extensions to download. i.e. 'bmp', 'gif'.
        """

        ls_get_exts = []

        for s_ext in s_exts:
            s_ext = s_ext.lower()
            ls_get_exts.append(s_ext)

        self._ls_get_exts = tuple(ls_get_exts)

    def set_recursive(self):
        self._b_recursive = True

    def set_source(self, s_type, s_host, s_root):
        """
        Method to define the source itself.

        :param s_type: Type of source. 'dir' for directories, 'ftp' for FTP, and 'smb' for Samba.

        :param s_host: Address of the source. i.e. '192.168.0.100'

        :param s_root: Root folder of the source. i.e. '/emulator-data/screenshots/'
        """

        # Type of source
        if s_type in ('dir', 'ftp', 'smb'):
            self._s_type = s_type
        else:
            print 'ERROR: Unknown source type "%s"' % s_type

        # Host address
        self._s_host = s_host

        # Root
        self._s_root = s_root

    def set_user_pass(self, s_user, s_pass):
        self._s_user = s_user
        self._s_pass = s_pass


#=======================================================================================================================
#=======================================================================================================================
class Ftp:
    """
    Short class (it's not meant to give you full control of FTPs) to handle FTP sources to be included inside the
    meta-class ShotSource. Basically it's a wrapper class for python 'official' library ftplib.
    """
    def __init__(self, s_host, s_user, s_pass, i_timeout):

        self.b_connected = False

        try:
            self.o_ftp = ftplib.FTP(host=s_host, user=s_user, passwd=s_pass, timeout=i_timeout)
            self.b_connected = True

        except ftplib.all_errors:
            self.o_ftp = None

    def _delete_file(self, o_file_entry):
        """
        Method to delete a file from the ftp server.

        :param o_file_entry: I must be a real file entry (self._s_type = 'f'). Otherwise an error is printed.

        :return: Nothing.
        """
        if o_file_entry.is_file():
            s_original_path = self.o_ftp.pwd()
            self.o_ftp.cwd(o_file_entry.s_root)

            #self.o_ftp._sendcmd('TYPE I')
            self.o_ftp.delete(o_file_entry.s_full_name)

            self.o_ftp.cwd(s_original_path)

    def _delete_dir(self, o_file_entry):

        b_deleted = False

        if o_file_entry.s_type == 'd':
            # BIG WARNING HERE: After deleting a directory you are returned to the parent folder of the deleted one!!!
            self.o_ftp.cwd(o_file_entry.s_root)
            try:
                self.o_ftp.rmd(o_file_entry.s_full_name)
                b_deleted = True
            except ftplib.error_perm:
                pass

        return b_deleted

    @staticmethod
    def _file_entry_from_nlst_line(s_root, s_nlst_line):
        """
        Method to build a File Entry (given by fentry.py) parsing a nlst line.

        :param s_nlst_line: line given by ftp nlst command '-rwxrwxrwx   1 root  root    700 Oct 30 19:45 syslink.dat'

        :return:
        """

        o_file_entry = fentry.FileEntry()

        if s_nlst_line != '..':

            # Type of entry (directory or file) and permissions
            s_chunk_1 = s_nlst_line.partition('   ')[0]

            if s_chunk_1[0] == 'd':
                o_file_entry.s_type = 'd'
            else:
                o_file_entry.s_type = 'f'

            o_file_entry.s_permission = s_chunk_1[1:]

            # Ownership
            s_chunk_2 = s_nlst_line.partition('    ')[0][15:]

            o_file_entry.s_user = s_chunk_2.partition('  ')[0]
            o_file_entry.s_group = s_chunk_2.partition('  ')[2]

            # Size, Date and file name
            s_chunk_3 = s_nlst_line.partition('    ')[2]

            o_file_entry.set_size(int(s_chunk_3.partition(' ')[0]))
            o_file_entry.set_name(s_chunk_3.split(' ')[4])

            # Root and Full Path
            o_file_entry.set_root(s_root)

        return o_file_entry

    def list_file_entries(self, s_root='', lo_prev_elements=[], b_recursive=False):
        """
        Method to return a list containing all the FtpFileEntry objects corresponding to the elements in the CWD of the
        ftp.

        :return: A list of FtpFileEntry objects.
        """

        if self.b_connected:

            s_current_dir = self.o_ftp.pwd()

            if s_root != '':
                self.o_ftp.cwd(s_root)

            for s_line in self.o_ftp.nlst():

                o_file_entry = self._file_entry_from_nlst_line(s_root, s_line)

                 # Only actual files, 'f', and directories, 'd' are kept. Fake dirs like '..' are avoid.
                if o_file_entry.is_file() or o_file_entry.is_dir():
                    lo_prev_elements.append(o_file_entry)

                    if b_recursive:
                        if o_file_entry.is_dir():
                            self.list_file_entries(o_file_entry.s_full_path, lo_prev_elements, b_recursive=True)

            self.o_ftp.cwd(s_current_dir)

        return lo_prev_elements

    def download_file(self, o_file_entry, s_dest):
        if o_file_entry.s_type == 'f':
            s_original_path = self.o_ftp.pwd()
            self.o_ftp.cwd(o_file_entry.s_root)

            s_dst_path = os.path.join(s_dest, o_file_entry.s_full_name)

            o_download_file = open(s_dst_path, 'wb')

            self.o_ftp.sendcmd('TYPE I')
            s_command = 'RETR %s' % o_file_entry.s_full_name
            self.o_ftp.retrbinary(s_command, o_download_file.write)

            o_download_file.close()

            self.o_ftp.cwd(s_original_path)

        elif o_file_entry.s_type == 'd':
            print 'ERROR: You are trying to download_file a directory as a file'
            sys.exit()

        else:
            print 'ERROR: You are downloading an unknown o_file_entry "%s"' % o_file_entry.s_type
            sys.exit()

    def delete(self, o_file_entry):

        b_deleted = False

        if o_file_entry.is_file == 'f':
            b_deleted = self._delete_file(o_file_entry)
        elif o_file_entry.is_dir == 'd':
            b_deleted = self._delete_dir(o_file_entry)

        return b_deleted


#=======================================================================================================================
#=======================================================================================================================
class Dir:
    def __init__(self, s_root):
        if os.path.isdir(s_root):
            self.b_connected = True
            self.s_root = s_root
        else:
            self.b_connected = False
            self.s_root = ''

    @staticmethod
    def _file_entry_from_path(s_path):

        o_file_entry = fentry.FileEntry()

        # Full path, name and extension
        o_file_entry.s_full_path = s_path
        o_file_entry.set_name(os.path.basename(s_path))
        o_file_entry.s_root = os.path.split(s_path)[0]

        # File or dir
        if os.path.isdir(s_path):
            o_file_entry.s_type = 'd'
        elif os.path.isfile(s_path):
            o_file_entry.s_type = 'f'

        # Size
        o_file_entry.set_size(files.get_size_of(s_path))

        # Date
        o_file_entry.f_time = os.path.getmtime(s_path)

        # todo: obtain user/group, permission and date from files
        #print o_file_entry

        return o_file_entry

    def list_file_entries(self, s_root='', lo_prev_elements=[], b_recursive=False):

        if s_root == '':
            s_root = self.s_root

        for s_element in os.listdir(s_root):
            s_full_path = os.path.join(s_root, s_element)

            o_file_entry = self._file_entry_from_path(s_full_path)

            lo_prev_elements.append(o_file_entry)

            if o_file_entry.is_dir() and b_recursive:
                self.list_file_entries(s_full_path, lo_prev_elements, b_recursive)

        return lo_prev_elements

    @staticmethod
    def download_file(o_file_entry, s_dst_dir, s_dst_name=''):
        s_src_file = o_file_entry.s_full_path
        if s_dst_name == '':
            s_dst_file = os.path.join(s_dst_dir, o_file_entry.s_full_name)
        else:
            s_dst_file = os.path.join(s_dst_dir, s_dst_name)

        shutil.copy(s_src_file, s_dst_file)

    def delete(self, o_file_entry):
        pass