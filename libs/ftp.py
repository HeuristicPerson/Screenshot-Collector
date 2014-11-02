"""
Small FTP library. It contains the Ftp class which is used to connect and perform different actions in a FTP and a
FtpFileEntry which is used to handle the contents of the ftp (download/delete are the main actions). Two twin libraries
come with this one to handle samba file entries and standard directory file entries.

The purpose of those three libraries is having the same methods for file entries in FTP, Samba and Standard directories.
So, the image collector can define different sources for screenshots and can interact with them no matter what they are.

(I'm pretty sure a good programmer could do this in a much more simple/fancy way. But this the way I know to do it...
"""

import ftplib
import os
import re
import sys

import fentry


class Ftp:
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

    def pwd(self):
        """
        Method to get the current working directory of the ftp.

        :return: An string indicating the current directory. i.e. '/abc/foo/'
        """

        return self.o_ftp.pwd()

    def list_elements(self, s_root='', lo_prev_elements=[], b_recursive=False):
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
                            self.list_elements(o_file_entry.s_full_path, lo_prev_elements, b_recursive=True)

            self.cwd(s_current_dir)

        return lo_prev_elements

    def _file_entry_from_nlst_line(self, s_root, s_nlst_line):
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

        lo_elements = self.list_elements(s_root)

        lo_files = []

        for o_element in lo_elements:
            if o_element.s_type == 'f':
                lo_files.append(o_element)

        return lo_files

    def download(self, o_file_entry, s_dest, s_mode='flat'):
        if o_file_entry.s_type == 'f':
            self._download_file(o_file_entry, s_dest, s_mode)
        elif o_file_entry.s_type == 'd':
            # todo: create a proper download method for ftp directories
            pass
        else:
            print 'ERROR: You are downloading an unknown o_file_entry "%s"' % o_file_entry.s_type


    def _download_file(self, o_file_entry, s_dest, s_mode='flat'):
        """
        Method to download a file from the ftp server. The file is downloaded without any kind of folder structure to
        the same place where the script is being executed from.

        :param o_file_entry: I must be a real file entry (self.s_type = 'f'). Otherwise an error is printed.

        :param s_dest: Destination folder for the file. i.e. '/home/john/downloads'

        :param s_mode: 'flat' or 'tree', with 'tree' you replicate the structure of folders present in the ftp in your
                       local computer. With 'flat' all the files are downloaded in the same folder.

        :return: Nothing.
        """

        if o_file_entry.s_type == 'f':
            s_original_path = self.o_ftp.pwd()
            self.o_ftp.cwd(o_file_entry.s_root)

            if s_mode == 'flat':
                s_dst_path = os.path.join(s_dest, o_file_entry.s_full_name)
            elif s_mode == 'tree':
                s_dst_path = os.path.join(s_dest, o_file_entry.s_root, o_file_entry.s_full_name)
            else:
                print 'ERROR: You are trying to download a file with unknown s_mode = %s' % s_mode
                sys.exit()

            o_download_file = open(s_dst_path, 'wb')

            s_command = 'RETR %s' % o_file_entry.s_full_name

            self.o_ftp.sendcmd('TYPE I')
            self.o_ftp.retrbinary(s_command, o_download_file.write)

            o_download_file.close()

            self.o_ftp.cwd(s_original_path)

        elif o_file_entry.s_type == 'd':
            print 'ERROR: You are trying to download a directory as a file'

        else:
            print 'ERROR: You are trying to download a non-existent file entry'

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

            #self.o_ftp.sendcmd('TYPE I')
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
            self.o_ftp.rmd(o_file_entry.s_full_name)

        elif o_file_entry.s_type == 'f':
            print 'ERROR: You are trying to delete a file as a directory'
        else:
            print 'ERROR: You are trying to delete a non-existent file entry as a directory'

    def sendcmd(self, s_cmd):
        self.o_ftp.sendcmd(s_cmd)

    def retrbinary(self, s_cmd, s_callback, i_blocksize=8192, i_rest=None):
        self.o_ftp.retrbinary(cmd=s_cmd, callback=s_callback, blocksize=i_blocksize, rest=i_rest)