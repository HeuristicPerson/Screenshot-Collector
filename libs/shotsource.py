import ftp
import os

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
        self.ls_get_exts = ('')     # File extensions to download (case insensitive). i.e. ('jpg', 'png')
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

    def _list_elements(self):
        """
        Method to list all the elements present in the source.
        :return:
        """

        lo_file_entries = []

        if self.b_connected:

            if self.s_type == 'dir':
                pass

            elif self.s_type == 'ftp':
                lo_file_entries = self.o_source.list_elements(self.s_root, b_recursive=self.b_recursive)

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
            self.b_connected = True

        elif self.s_type == 'ftp':
            self.o_source = ftp.Ftp(self.s_host, self.s_user, self.s_pass, 5)
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

    def download(self, s_dest, s_mode='flat'):
        """
        Method to download all the screenshots from a source.

        :param s_dest: Destination for the images. i.e. '/home/john/temp-images'

        :param s_mode:
        :return:
        """
        print 'Downloading images from: %s (%s)' % (self.s_name, self.s_host)
        print '------------------------------------------------------'

        # todo: I don't think it makes any sense to have a s_mode parameter. Always flat...

        self._connect()

        lo_file_entries = self._list_elements()

        i_files_downloaded = 0
        i_bytes_downloaded = 0
        i_files_deleted = 0
        i_bytes_deleted = 0
        i_dirs_deleted = 0

        for o_file_entry in lo_file_entries:
            if o_file_entry.s_type == 'f' and o_file_entry.s_ext in self.ls_get_exts:
                print 'Downloading: %s  %s' % (o_file_entry.s_full_name, o_file_entry.s_size)
                self.o_source.download(o_file_entry, s_dest, s_mode)
                i_files_downloaded += 1
                i_bytes_downloaded += o_file_entry.i_size


            if o_file_entry.s_type == 'f' and o_file_entry.s_ext.lower() in self.ls_del_exts:
                print '   Deleting: %s  %s' % (o_file_entry.s_full_name, o_file_entry.s_size)
                self.o_source.delete(o_file_entry)
                i_files_deleted += 1
                i_bytes_deleted += o_file_entry.i_size

            if o_file_entry.s_type == 'd' and not self.b_dir_keep:
                self.o_source.delete(o_file_entry)
                i_dirs_deleted += 1

        print '    Files downloaded: %i (%s)' % (i_files_downloaded, fentry.human_size(i_bytes_downloaded))
        print '       Files deleted: %i (%s)' % (i_files_deleted, fentry.human_size(i_bytes_deleted))
        print '        Dirs deleted: %i' % i_dirs_deleted
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

        for s_src_file in files.get_files_in(s_src_dir):
            s_orig_name, s_orig_ext = files.get_name_and_extension(s_src_file)

            s_new_name = shotname.raw_to_historic(s_orig_name, o_games_db)

            s_src_img = os.path.join(s_src_dir, s_src_file)
            s_dst_img = os.path.join(s_dst_dir, '%s.%s' % (s_new_name, self.s_hist_ext))

            s_cmd = 'convert "%s" "%s" 2>/dev/null' % (s_src_img, s_dst_img)
            os.system(s_cmd)
            os.remove(s_src_img)

            print 'Converted %s' % s_src_file
            print '       to %s' % s_dst_img

    def find_dat_file(self, s_folder):
        """
        Method to find the dat file in one folder.

        :param s_folder:

        :return:
        """

        s_dat_file = os.path.join(s_folder, '%s.txt' % self.s_name)
        if os.path.isfile(s_dat_file):
            self.s_dat_file = s_dat_file




