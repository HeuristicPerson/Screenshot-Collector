from libs import ftpextra

# Configuration - Basics
#=======================================================================================================================
s_TEMP_FOLDER = 'foo'
s_HISTORIC_FOLDER = 'foo'


# Configuration - FTPs
#=======================================================================================================================
lo_ftp_configs = []

# Xbox 360 FTP configuration
o_ftp_cfg_xbox360 = ftpextra.FtpCfg()
o_ftp_cfg_xbox360.s_name = 'xbox360'
o_ftp_cfg_xbox360.s_host = '192.168.0.106'
o_ftp_cfg_xbox360.s_user = 'xbox'
o_ftp_cfg_xbox360.s_pass = 'xbox'
o_ftp_cfg_xbox360.s_root = '/Hdd1/Freestyle Dash/Plugins/UserData'
o_ftp_cfg_xbox360.ls_get_extensions = ('bmp')
o_ftp_cfg_xbox360.ls_del_extensions = ('meta')
o_ftp_cfg_xbox360.b_recursive = True
o_ftp_cfg_xbox360.b_file_keep = True
o_ftp_cfg_xbox360.b_dir_keep = True

lo_ftp_configs.append(o_ftp_cfg_xbox360)


# FTP image gathering
#=======================================================================================================================
print 'Screenshot gatherer v0.1'
print '========================'

for o_ftp_config in lo_ftp_configs:
    o_ftp = ftpextra.Ftp(o_ftp_config)
    if o_ftp.b_connected:
        print 'FTP: %s (%s) connected' % (o_ftp_config.s_name, o_ftp.s_host)
        print '-----------------'
        o_ftp_elements = o_ftp.list_elements(o_ftp_config.s_root, b_recursive=True)
        for o_ftp_element in reversed(o_ftp_elements):
            print o_ftp_element
    else:
        print 'FTP: %s (%s) NOT connected' % (o_ftp_config.s_name, o_ftp.s_host)
        print '---------------------'