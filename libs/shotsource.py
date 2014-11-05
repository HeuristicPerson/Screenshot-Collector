import ftplib
import os
import sys

import fentry
import files
import gamecache
import shotname


class ShotSource():
    """
    Class to archive information about a source (ftp, folder, samba folder... maybe more in the future) where screenshots
    can be found.
    """

    def __init__(self):
        self.s_name = ''            # Name of the source (this name is going to be used to check the id->title database)
        self.s_type = ''            # Type of source ('folder', 'ftp', 'samba' by now)
        self.s_host = ''            # Host. i.e. '192.168.0.100'
        self.s_user = ''            # The name of the user of the FTP. i.e. 'john'
        self.s_pass = ''            # The password for the user. i.e. '123456'
        self.s_root = ''            # Root folder of the FTP where screenshots are located. i.e. '/data/screenshots/'
        self.i_timeout = 5          # Timeout
        self.ls_get_exts = ('')     # File extensions to download_file (case insensitive). i.e. ('jpg', 'png')
        self.ls_del_exts = ('')     # File extensions to delete (case insensitive). i.e. ('bak', 'txt')
        self.b_recursive = True     # Should search in sub-folders inside the root folder?
        self.b_dir_keep = True      # Should the empty folders be kept in the FTP?
        self.o_source = None        # The real source behind the MetaObject
        self.b_connected = False    # Is the source connected?
        self.s_hist_ext = ''        # Extension for the archived screenshots

        self.s_dat_file = ''        # Name of the dat file

        # Forcing the extensions to be lowercase so we can compare later just lowercase extensions making the mechanism
        # to be case insensitive.
        ls_new_get_exts = []
        for s_get_ext in self.ls_get_exts:
            s_get_ext = s_get_ext.lower()
            ls_new_get_exts.append(s_get_ext)

        self.ls_get_exts = ls_new_get_exts

        ls_new_del_exts = []
        for s_del_ext in self.ls_del_exts:
            s_del_ext = s_del_ext.lower()
            ls_new_del_exts.append(s_del_ext)

        self.ls_del_exts = ls_new_del_exts

    def __str__(self):
        s_output = '%s, %s source at %s' % (self.s_name, self.s_type, self.s_host)
        return s_output

    def _list_file_entries(self):
        """
        Method to list all the elements present in the source.
        :return:
        """

        lo_file_entries = []

        if self.b_connected:

            if self.s_type == 'dir':
                lo_file_entries = self.o_source.list_file_entries()

            elif self.s_type == 'ftp':
                lo_file_entries = self.o_source.list_file_entries(self.s_root, b_recursive=self.b_recursive)

            elif self.s_type == 'samba':
                pass

        # Since the list of elements could be used to delete everything, it's needed that it's reversed to list first
        # the childs and then the parents. This way you will delete first the childs and then the parents. The opposite
        # order would lead you to a situation where you would be trying to delete a folder while it stills had the
        # content inside.
        return reversed(lo_file_entries)

    def _connect(self):
        if self.s_type == 'dir':
            # todo: add support for folders
            self.o_source = directory.Dir()
            self.b_connected = True

        elif self.s_type == 'ftp':
            self.o_source = Ftp(self.s_host, self.s_user, self.s_pass, 5)
            self.b_connected = True

        elif self.s_type == 'samba':
            # todo: add support for samba remote folders
            pass

    def _disconnect(self):
        """
        Method to _disconnect the source.

        :return: Nothing.
        """

        self.o_source = None
        self.b_connected = False

    def download_files(self, s_dest):
        """
        Method to download_file all the screenshots from a source.

        :param s_dest: Destination for the images. i.e. '/home/john/temp-images'

        :return: Nothing
        """

        print 'Downloading images from: %s (%s)' % (self.s_name, self.s_host)
        print '------------------------------------------------------'

        self._connect()

        lo_file_entries = self._list_file_entries()

        i_files_downloaded = 0
        i_bytes_downloaded = 0
        i_files_deleted = 0
        i_bytes_deleted = 0
        i_dirs_deleted = 0

        for o_file_entry in lo_file_entries:
            if o_file_entry.s_type == 'f' and o_file_entry.s_ext in self.ls_get_exts:
                print 'Downloaded: %s  %s' % (o_file_entry.s_full_name, o_file_entry.s_size)
                self.o_source.download_file(o_file_entry, s_dest)
                i_files_downloaded += 1
                i_bytes_downloaded += o_file_entry.i_size

            if o_file_entry.s_type == 'f' and o_file_entry.s_ext.lower() in self.ls_del_exts:
                print '   Deleted: %s  %s' % (o_file_entry.s_full_name, o_file_entry.s_size)
                self.o_source.delete(o_file_entry)
                i_files_deleted += 1
                i_bytes_deleted += o_file_entry.i_size

            if o_file_entry.s_type == 'd' and not self.b_dir_keep:
                self.o_source.delete(o_file_entry)
                i_dirs_deleted += 1

        print '            Files downloaded: %i (%s)' % (i_files_downloaded, files.human_size(i_bytes_downloaded))
        print '               Files deleted: %i (%s)' % (i_files_deleted, files.human_size(i_bytes_deleted))
        print '                Dirs deleted: %i' % i_dirs_deleted
        print

        self._disconnect()

    def archive(self, s_src_dir, s_dst_dir):
        """
        Method to rename, convert and archive the images found in s_src_dir, to s_dst_dir

        :param s_src_dir: Source directory. i.e. '/home/john/temp'
        :param s_dst_dir: Destination directory. i.e. '/home/john/screenshot-archive'
        :return:
        """
        print 'Archiving images from: %s (%s)' % (self.s_name, self.s_host)
        print '------------------------------------------------------'

        o_games_db = gamecache.Database(self.s_name, self.s_dat_file)

        i_files_processed = 0
        i_orig_size = 0
        i_mod_size = 0

        for s_src_file in files.get_files_in(s_src_dir):
            s_orig_name, s_orig_ext = files.get_name_and_extension(s_src_file)

            s_dst_file = '%s.%s' % (shotname.raw_to_historic(s_orig_name, o_games_db), self.s_hist_ext)

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

    def find_dat_file(self, s_folder):
        """
        Method to find the dat file in one folder.

        :param s_folder:

        :return:
        """

        s_dat_file = os.path.join(s_folder, '%s.txt' % self.s_name)
        if os.path.isfile(s_dat_file):
            self.s_dat_file = s_dat_file


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

    def cwd(self, s_dirname):
        # todo: add error handling code when s_dirname doesn't exist
        self.o_ftp.cwd(s_dirname)

    def list_file_entries(self, s_root='', lo_prev_elements=[], b_recursive=False):
        """
        Method to return a list containing all the FtpFileEntry objects corresponding to the elements in the CWD of the
        ftp.

        :return: A list of FtpFileEntry objects.
        """

        if self.b_connected:

            s_current_dir = self.o_ftp.pwd()

            if s_root != '':
                self.cwd(s_root)

            for s_line in self.o_ftp.nlst():

                o_file_entry = self._file_entry_from_nlst_line(s_root, s_line)

                 # Only actual files, 'f', and directories, 'd' are kept. Fake dirs like '..' are avoid.
                if o_file_entry.s_type in ('f', 'd'):
                    lo_prev_elements.append(o_file_entry)

                    if b_recursive:
                        if o_file_entry.s_type == 'd':
                            self.list_file_entries(o_file_entry.s_full_path, lo_prev_elements, b_recursive=True)

            self.cwd(s_current_dir)

        return lo_prev_elements

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

    def list_dirs(self, s_root):
        """
        Similar to list_elements method but only directory elements are returned.

        :return: A list of FtpFileEntry objects.
        """

        lo_elements = self.list_elements(s_root)

        lo_dirs = []

        for o_element in lo_elements:
            if o_element.s_type == 'd':
                lo_dirs.append(o_element)

        return lo_dirs

    def list_files(self, s_root):
        """
        Similar to list_elements method but only file elements are returned.

        :return: A list of FtpFileEntry objects.
        """

        lo_elements = self.list_file_entries(s_root)

        lo_files = []

        for o_element in lo_elements:
            if o_element.s_type == 'f':
                lo_files.append(o_element)

        return lo_files

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
        if o_file_entry.s_type == 'f':
            self._delete_file(o_file_entry)
        elif o_file_entry.s_type == 'd':
            self._delete_dir(o_file_entry)

    def _delete_file(self, o_file_entry):
        """
        Method to delete a file from the ftp server.

        :param o_file_entry: I must be a real file entry (self.s_type = 'f'). Otherwise an error is printed.

        :return: Nothing.
        """
        if o_file_entry.s_type == 'f':
            s_original_path = self.o_ftp.pwd()
            self.o_ftp.cwd(o_file_entry.s_root)

            #self.o_ftp._sendcmd('TYPE I')
            self.o_ftp.delete(o_file_entry.s_full_name)

            self.o_ftp.cwd(s_original_path)

        elif o_file_entry.s_type == 'd':
            print 'ERROR: You are trying to delete a directory as a file'
        else:
            print 'ERROR: You are trying to delete a non-existent file entry'

    def _delete_dir(self, o_file_entry):

        if o_file_entry.s_type == 'd':
            # BIG WARNING HERE: After deleting a directory you are returned to the parent folder of the deleted one!!!
            self.o_ftp.cwd(o_file_entry.s_root)
            try:
                self.o_ftp.rmd(o_file_entry.s_full_name)
            except ftplib.error_perm:
                pass

        elif o_file_entry.s_type == 'f':
            print 'ERROR: You are trying to delete a file as a directory'
        else:
            print 'ERROR: You are trying to delete a non-existent file entry as a directory'