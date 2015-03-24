#!/usr/local/bin/python
# -*- coding: utf8 -*-

"""
Library to handle in a common way different sources (ftp, dirs and samba dirs) for screenshots.
"""


import datetime
import ftplib
import os
import smbc             # Library to work Samba Shares. Check doc here https://pythonhosted.org/pysmbc/smbc-module.html
import shutil

import cons
import fentry
import fileutils
import gamecache
import shotname


class ShotSource():
    """
    Class to archive_files information about a source (ftp, folder, samba folder... maybe more in the future) where
    screenshots can be found.
    """

    def __init__(self, u_name):
        self.u_name = u_name               # Name of the source

        self._u_dat_file = u''             # Name of the dat file
        self._u_src_scheme = u''           # Source naming scheme (emulators have different screenshot naming schemes)

        self._u_type = u''                 # Type of source ('dir', 'ftp', 'smb' by now)
        self._u_host = u''                 # Host. i.e. '192.168.0.100'
        self._u_root = u''                 # Root folder of the FTP where screenshots are located. i.e. '/data/'

        self._u_user = u''                 # The name of the user of the FTP. i.e. 'john'
        self._u_pass = u''                 # The password for the user. i.e. '123456'

        self._i_timeout = 5                # Timeout

        self._lu_get_exts = []             # File exts to download_file (case insensitive). i.e. ('jpg', 'png')
        self._lu_del_exts = []             # File exts to delete (case insensitive). i.e. ('bak', 'txt')

        self._b_recursive = True           # Should search in sub-folders inside the root folder?
        self._b_dir_keep = True            # Should the empty folders be kept in the FTP?
        self.o_source = None               # The real source behind the MetaObject
        self.b_connected = False           # Is the source connected?

        self.u_hist_ext = cons.u_HIST_EXT  # Extension for the archived screenshots

    def __str__(self):
        u_output = u''
        u_output += u'<SOURCE OBJECT>\n'
        u_output += u'         u_name: %s\n' % self.u_name
        u_output += u'    _u_dat_file: %s\n' % self._u_dat_file
        u_output += u'  _u_src_scheme: %s\n' % self._u_src_scheme
        u_output += u'        u_type: %s\n' % self._u_type
        u_output += u'        _u_host: %s\n' % self._u_host
        u_output += u'        _u_root: %s\n' % self._u_root
        u_output += u'        _u_user: %s\n' % self._u_user
        u_output += u'        _u_pass: %s\n' % self._u_pass
        u_output += u'     _i_timeout: %i\n' % self._i_timeout
        u_output += u'   _lu_get_exts: %s\n' % str(self._lu_get_exts)
        u_output += u'   _lu_del_exts: %s\n' % str(self._lu_del_exts)
        u_output += u'   _b_recursive: %s\n' % str(self._b_recursive)
        u_output += u'    _b_dir_keep: %s\n' % str(self._b_dir_keep)
        u_output += u'       o_source: %s\n' % str(self.o_source)
        u_output += u'    b_connected: %s\n' % str(self.b_connected)

        return u_output.encode('ascii', 'strict')

    def _list_file_entries(self):
        """
        Method to list all the File Entry elements present in the source.
        :return:
        """

        lo_file_entries = []

        if self.b_connected:

            if self._u_type in (u'dir', u'ftp', u'smb'):
                lo_file_entries = self.o_source.list_file_entries(self._u_root,
                                                                  lo_file_entries,
                                                                  b_recursive=self._b_recursive)

            else:
                raise Exception('ERROR: Unknown source type "%s"' % self._u_type)

        # Since the list of elements could be used to delete everything, it's needed that it's reversed to list first
        # the children and then the parents. This way you will delete first the children and then the parents. The
        # opposite order would lead you to a situation where you would be trying to delete a folder while it stills had
        # the content inside.
        return reversed(lo_file_entries)

    def _connect(self):

        if self._u_type == u'dir':
            self.o_source = Dir(self._u_root)
            self.b_connected = True

        elif self._u_type == u'ftp':
            self.o_source = Ftp(self._u_host, self._u_user, self._u_pass, 5)
            self.b_connected = self.o_source.b_connected
            if not self.b_connected:
                print 'FTP: Not connected'

        elif self._u_type == u'smb':
            # WIP: add support for samba remote folders
            self.o_source = Smb(self._u_host, self._u_user, self._u_pass, 5)
            self.b_connected = self.o_source.b_connected

        else:
            s_message = 'ERROR: Can\'t connect to unknown ShotSource.u_type = %s' % self._u_type.encode('ascii', 'strict')
            raise Exception(s_message)

    def _disconnect(self):
        """
        Method to _disconnect the source.

        :return: Nothing.
        """

        self.o_source = None
        self.b_connected = False

    def archive_files(self, u_src_dir, u_dst_dir):
        """
        Method to rename, convert and archive_files the images found in u_src_dir, to u_dst_dir

        :param u_src_dir: Source directory. i.e. '/home/john/temp'

        :param u_dst_dir: Destination directory. i.e. '/home/john/screenshot-archive_files'

        :return: Nothing
        """

        u_message = u'Archiving images from: %s (%s, %s)' % (self.u_name, self._u_type, self._u_host)
        print u_message.encode('ascii', 'strict')
        print '-' * 78

        # We build the full database file path and we create a database object from it
        u_db_path = os.path.join(cons.u_DAT_DIR, u'%s.txt' % self._u_dat_file)
        o_games_db = gamecache.Database(u_db_path)

        # Initialization
        i_files_processed = 0
        i_orig_size = 0
        i_mod_size = 0

        # Processing each file found
        for u_src_file in fileutils.get_files_in(u_src_dir):
            u_orig_name, u_orig_ext = fileutils.get_name_and_extension(u_src_file)

            u_arch_name = shotname.raw_to_historic(o_games_db, u_orig_name)

            u_dst_file = u'%s.%s' % (u_arch_name, self.u_hist_ext)

            u_src_img = os.path.join(u_src_dir, u_src_file)
            u_dst_img = os.path.join(u_dst_dir, u_dst_file)

            s_cmd = 'convert "%s" "%s" 2>/dev/null' % (u_src_img, u_dst_img)
            os.system(s_cmd)

            print 'Src: %s  %s' % (u_src_file, fileutils.human_size(fileutils.get_size_of(u_src_img)))
            print 'Dst: %s  %s\n' % (u_dst_file, fileutils.human_size(fileutils.get_size_of(u_dst_img)))

            i_files_processed += 1
            i_orig_size += fileutils.get_size_of(u_src_img)
            i_mod_size += fileutils.get_size_of(u_dst_img)

            os.remove(u_src_img)

        if i_orig_size != 0:
            s_ratio = '%0.1f%%' % (100.0 * i_mod_size / i_orig_size)
        else:
            s_ratio = '%0.1f%%' % 0.0

        s_report = 'Converted %i files from %s to %s (%s)\n' % (i_files_processed,
                                                            fileutils.human_size(i_orig_size),
                                                            fileutils.human_size(i_mod_size),
                                                            s_ratio)

        print s_report.rjust(78)

    def download_files(self, s_dst_dir):
        """
        Method to download_file all the screenshots from a source.

        :param s_dst_dir: Destination for the images. i.e. '/home/john/temp-images'

        :return: Nothing
        """

        print 'Getting images from: %s (%s, %s)' % (self.u_name, self._u_type, self._u_host)
        print '-' * 78

        self._connect()

        lo_remote_fentries = self._list_file_entries()

        i_remote_files = 0
        i_remote_dirs = 0

        for o_remote_file_entry in lo_remote_fentries:
            if o_remote_file_entry.is_file():
                i_remote_files += 1
            elif o_remote_file_entry.is_dir():
                i_remote_dirs += 1

        # Workaround to get the database name using a file entry object instead of directly parse the database file
        # path.
        o_db_fentry = fentry.FileEntry()
        o_db_fentry.from_local_path(self._u_dat_file)
        u_db_name = o_db_fentry.u_name

        i_files_got = 0
        i_bytes_got = 0
        i_files_del = 0
        i_bytes_del = 0
        i_dirs_del = 0

        for o_remote_fentry in lo_remote_fentries:

            # Downloading + Renaming of files with selected extensions
            if o_remote_fentry.is_file() and o_remote_fentry.u_ext in self._lu_get_exts:

                # Adding extra information (timestamp, database name, and source naming scheme) seems to be a good idea
                # to be safe. i.e. something fails and you end with a lot of mixed files from many different sources in
                # your temp folder
                u_dst_name = u'%s - %s %s - %s' % (o_remote_fentry.get_human_date(),
                                                   u_db_name, self._u_src_scheme,
                                                   o_remote_fentry.u_full_name)

                u_message = u'Found: %s  %s' % (o_remote_fentry.u_full_name, o_remote_fentry.u_size)
                print u_message.encode('utf8', 'strict')

                if self.o_source.download_file(o_remote_fentry, s_dst_dir, u_dst_name):

                    print 'Wrote: %s' % u_dst_name.encode('ascii', 'strict')

                    i_files_got += 1
                    i_bytes_got += o_remote_fentry.i_size

                else:
                    print 'ERROR: Couldn\'t write %s' % u_dst_name.encode('ascii', 'strict')

            # Deletion of files with selected extensions
            # TODO: If a file hasn't been downloaded, it MUST NOT be deleted. Otherwise it would be lost FOREVER.
            if o_remote_fentry.is_file() and o_remote_fentry.u_ext.lower() in self._lu_del_exts:
                if self.o_source.delete(o_remote_fentry):
                    print 'Del: %s  %s' % (o_remote_fentry.u_full_name, o_remote_fentry.s_size)
                    i_files_del += 1
                    i_bytes_del += o_remote_fentry.i_size

            # Removal of empty folders
            if o_remote_fentry.is_dir() and not self._b_dir_keep:
                if self.o_source.delete(o_remote_fentry):
                    i_dirs_del += 1

            print

        s_report = ''
        s_report += 'Got: %i/%i files (%s) ' % (i_files_got, i_remote_files, fileutils.human_size(i_bytes_got))
        s_report += 'Del: %i/%i files (%s) '% (i_files_del, i_remote_files, fileutils.human_size(i_bytes_del))
        s_report += 'and %i/%i dirs\n' % (i_dirs_del, i_remote_dirs)

        print s_report.rjust(78)

        self._disconnect()

    def set_clean_dirs(self):
        self._b_dir_keep = False

    def set_db_and_scheme(self, s_db, s_scheme):
        self._u_dat_file = s_db
        self._u_src_scheme = s_scheme

    def set_del_exts(self, *s_exts):

        ls_del_exts = []

        for s_ext in s_exts:
            s_ext = s_ext.lower()
            ls_del_exts.append(s_ext)

        self._lu_del_exts = tuple(ls_del_exts)

    def set_get_exts(self, *s_exts):
        """
        Method to define the extensions to download/get from the source.

        :param: s_exts: List of extensions to download. i.e. 'bmp', 'gif'.
        """

        ls_get_exts = []

        for s_ext in s_exts:
            s_ext = s_ext.lower()
            ls_get_exts.append(s_ext)

        self._lu_get_exts = tuple(ls_get_exts)

    def set_recursive(self):
        self._b_recursive = True

    def set_source(self, u_type, u_host, u_root):
        """
        Method to define the source itself.

        :param u_type: Type of source. 'dir' for directories, 'ftp' for FTP, and 'smb' for Samba.

        :param u_host: Address of the source. i.e. '192.168.0.100'

        :param u_root: Root folder of the source. i.e. '/emulator-data/screenshots/'
        """

        # Type of source
        if u_type in (u'dir', u'ftp', u'smb'):
            self._u_type = u_type
        else:
            raise Exception('ERROR: Unknown source type "%s"' % u_type)

        # Host address
        if u_type == u'smb':
            self._u_host = u'smb://%s' % u_host
        else:
           self._u_host = u_host

        # Root
        self._u_root = u_root

    def set_user_pass(self, u_user, u_pass):
        """
        Method to set the user/password combination for the source.

        :param u_user: User name for the source (for those which require it: ftp, smb). i.e. 'john'.

        :param u_pass: Password for the source (same comment than above). i.e. '123456'.

        :return: Nothing.
        """

        # TODO: Add extra checks

        self._u_user = u_user
        self._u_pass = u_pass


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

        :param o_file_entry: I must be a real file entry (self.u_type = 'f'). Otherwise an error is printed.

        :return: Nothing.
        """
        if o_file_entry.is_file():
            s_original_path = self.o_ftp.pwd()
            self.o_ftp.cwd(o_file_entry.s_root)

            #self.o_ftp._sendcmd('TYPE I')
            self.o_ftp.delete(o_file_entry.s_full_name)

            self.o_ftp.cwd(s_original_path)

            return True

    def _delete_dir(self, o_file_entry):

        b_deleted = False

        if o_file_entry.is_dir():
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
                o_file_entry.u_type = 'd'
            else:
                o_file_entry.u_type = 'f'

            o_file_entry.u_permission = s_chunk_1[1:]

            # Ownership
            s_chunk_2 = s_nlst_line.partition('    ')[0][15:]

            o_file_entry.u_user = s_chunk_2.partition('  ')[0]
            o_file_entry.u_group = s_chunk_2.partition('  ')[2]

            # Size and Full path (full path => root, name, ext)
            s_chunk_3 = s_nlst_line.partition('    ')[2]

            o_file_entry.set_size(int(s_chunk_3.partition(' ')[0]))

            s_name = s_chunk_3.split(' ')[4]
            s_full_path = os.path.join(s_root, s_name)
            o_file_entry.set_full_path(s_full_path)

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

                # Unfortunately, FTP nlst line doesn't provide full date information. So it's needed to send a FTP MDTM
                # command to get that information and then parse+add it to the o_file_entry object.
                if o_file_entry.is_file():
                    s_modified_time = self.o_ftp.sendcmd('MDTM %s' % o_file_entry.u_full_name).partition(' ')[2]
                    o_modified_time = datetime.datetime.strptime(s_modified_time, '%Y%m%d%H%M%S')
                    o_file_entry.f_time = (o_modified_time - datetime.datetime(1970, 1, 1)).total_seconds()

                if o_file_entry.is_file() or o_file_entry.is_dir():
                    lo_prev_elements.append(o_file_entry)

                    if b_recursive and o_file_entry.is_dir():
                        self.list_file_entries(o_file_entry.u_full_path, lo_prev_elements, b_recursive)

            self.o_ftp.cwd(s_current_dir)

        return lo_prev_elements

    def download_file(self, o_file_entry, s_dst_dir, s_dst_file=''):

        b_downloaded = False

        if o_file_entry.is_file():
            s_original_path = self.o_ftp.pwd()
            self.o_ftp.cwd(o_file_entry.s_root)

            if s_dst_file == '':
                s_dst_path = os.path.join(s_dst_dir, o_file_entry.s_full_name)
            else:
                s_dst_path = os.path.join(s_dst_dir, s_dst_file)

            try:
                o_download_file = open(s_dst_path, 'wb')

                self.o_ftp.sendcmd('TYPE I')
                s_command = 'RETR %s' % o_file_entry.s_full_name
                self.o_ftp.retrbinary(s_command, o_download_file.write)

                o_download_file.close()
            except:
                # TODO: Narrow the exception and add more informative messages in case of errors.
                print 'ERROR: I couldn\'t download the file'

            self.o_ftp.cwd(s_original_path)

        elif o_file_entry.is_dir():
            raise Exception('ERROR: You are trying to download_file a directory as a file')

        else:
            raise Exception('ERROR: You are downloading an unknown o_file_entry "%s"' % o_file_entry.s_type)

        return b_downloaded

    def delete(self, o_file_entry):

        b_deleted = False

        if o_file_entry.is_file():
            b_deleted = self._delete_file(o_file_entry)
        elif o_file_entry.is_dir():
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
        o_file_entry.u_full_path = s_path
        o_file_entry.set_name(os.path.basename(s_path))
        o_file_entry.u_root = os.path.split(s_path)[0]

        # File or dir
        if os.path.isdir(s_path):
            o_file_entry.u_type = 'd'
        elif os.path.isfile(s_path):
            o_file_entry.u_type = 'f'

        # Size
        o_file_entry.set_size(fileutils.get_size_of(s_path))

        # Date
        o_file_entry.f_time = os.path.getmtime(s_path)

        # todo: obtain user/group, permission and date from files
        #print o_file_entry

        return o_file_entry

    def list_file_entries(self, u_abs_root='', b_recursive=False):

        # Absolute and static root. If it's not specified, it's the source root folder.
        if u_abs_root == '':
            u_abs_root = self.s_root

        # Initialization of the list containing all the FileEntry objects
        lo_file_entries = []

        if b_recursive:
            # We get the full path of each file and we build a FileEntry object for each one.
            for u_dyn_root, lu_dirs, lu_files in os.walk(u_abs_root):

                for u_element in lu_files:
                    u_full_path = os.path.join(u_dyn_root, u_element)

                    o_file_entry = self._file_entry_from_path(u_full_path)
                    lo_file_entries.append(o_file_entry)

        else:
            for u_element in os.listdir(u_abs_root):
                u_full_path = os.path.join(u_abs_root, u_element)
                if os.path.isfile(u_full_path):
                    o_file_entry = self._file_entry_from_path(u_full_path)
                    lo_file_entries.append(o_file_entry)

        return lo_file_entries

    @staticmethod
    def download_file(o_file_entry, u_dst_dir, u_dst_name=''):
        s_src_file = o_file_entry.u_full_path
        if u_dst_name == '':
            s_dst_file = os.path.join(u_dst_dir, o_file_entry.s_full_name)
        else:
            s_dst_file = os.path.join(u_dst_dir, u_dst_name)

        try:
            shutil.copy(s_src_file, s_dst_file)
            b_downloaded = True
        except:
            b_downloaded = False

        return b_downloaded

    @staticmethod
    def delete(o_file_entry):
        """
        Method to delete files in the source.

        :param o_file_entry: File object (defined in XXX) to be deleted.

        :return:
        """
        try:
            os.remove(o_file_entry.u_full_path)
            return True
        except OSError:
            print '  Err: Failed to delete the file, check permissions\n'


#=======================================================================================================================
class Smb:
    """
    Short class (it's not meant to give you full control of FTPs) to handle FTP sources to be included inside the
    meta-class ShotSource. Basically it's a wrapper class for python 'official' library ftplib.
    """
    def __init__(self, u_host, u_user, u_pass, i_timeout):

        self.b_connected = False
        self._u_host = u_host
        # We store the user/password UNENCRYPTED, this is a NO-NO-NO... It just works for the purpose and scope of this
        # small project but NEVER do something like this if you have ANY concern about security.
        self._u_user = u_user
        self._u_pass = u_pass

        # First we prepare the connection
        self.o_smb = smbc.Context()
        self.o_smb.optionNoAutoAnonymousLogin = True
        self.o_smb.functionAuthData = self._authenticate

        # Then we check it's working
        try:
            self.o_smb.stat(u_host)
            self.b_connected = True

        except ValueError:
            print 'SMB: Not connected, check samba server'  # Error when the samba address doesn't exist
        except smbc.NoEntryError:
            print 'SMB: Not connected, check samba server'  # Error when the samba address doesn't exist
        except smbc.PermissionError:
            print 'SMB: Not connected, check user/password'   # Error when the access data is wrong.

    def _authenticate(self, server, u_share, u_workgroup, u_username, u_password):
        """
        Cheesy, dirty, and wacky function to authenticate in the samba server. DON'T TAKE IT SERIOUSLY... but it works
        :param server:
        :param share:
        :param workgroup:
        :param username:
        :param password:
        :return:
        """
        return ('', self._u_user, self._u_pass)

    def _delete_file(self, o_file_entry):
        """
        Method to delete a file from the ftp server.

        :param o_file_entry: I must be a real file entry (self.u_type = 'f'). Otherwise an error is printed.

        :return: Nothing.
        """

        b_file_deleted = False

        return b_file_deleted

    def _delete_dir(self, o_file_entry):

        b_dir_deleted = False

        return b_dir_deleted

    def list_file_entries(self, u_root=u'', lo_file_entries=[], b_recursive=False):
        """
        Method to return a list containing all the FtpFileEntry objects corresponding to the elements in the CWD of the
        ftp.

        :return: A list of FtpFileEntry objects.
        """

        # In order to access any folder we always have to include the name of the samba sare "self._u_host" at the
        # beginning of the real folder.
        u_base_path = os.path.join(self._u_host, u_root)

        o_smb_dir = self.o_smb.opendir(u_base_path)

        for o_element in o_smb_dir.getdents():

            # We create an empty file entry
            o_file_entry = fentry.FileEntry()

            # If the element found is a file (I don't know why but type 8 is file)
            if o_element.smbc_type == 8:
                u_file_path = os.path.join(u_base_path, o_element.name)

                o_file = self.o_smb.open(u_file_path)
                #print o_file.fstat()

                # We populate the file entry object with the required data
                o_file_entry.u_type = 'f'
                o_file_entry.set_full_path(u_file_path)
                o_file_entry.set_size(o_file.fstat()[6])

                # Last time modified (NOTICE fstat() method is rounded to seconds instead of the standard unix behaviour
                # where you get milliseconds. Not a big deal for my purpose.
                o_file_entry.f_time = o_file.fstat()[8]

                o_file.close()

            # If the element found is a directory, but not the default '.' or '..' directories
            elif (o_element.smbc_type == 7) and (o_element.name not in ('.', '..')):
                u_dir_path = os.path.join(u_base_path, o_element.name)

                #print u_dir_path

                # Population of the file entry with the required data
                o_file_entry.u_type = 'd'
                o_file_entry.set_full_path(u_dir_path)

            # If the file entry is a file or a VALID directory, it's added to the list of file entries
            if o_file_entry.is_file() or o_file_entry.is_dir():
                lo_file_entries.append(o_file_entry)

                if b_recursive and o_file_entry.is_dir():
                    u_sub_dir = os.path.join(u_root, o_element.name)
                    self.list_file_entries(u_sub_dir, lo_file_entries, b_recursive)

        return lo_file_entries

    def download_file(self, o_file_entry, s_dst_dir, s_dst_file=''):
        b_downloaded = False

        return b_downloaded

    def delete(self, o_file_entry):

        b_deleted = False

        return b_deleted

