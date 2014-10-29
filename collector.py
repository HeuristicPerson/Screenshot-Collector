from libs import ftpextra

# Configuration - Basics
#=======================================================================================================================
s_TEMP_FOLDER = 'foo'
s_HISTORIC_FOLDER = 'foo'


# Configuration - FTPs
#=======================================================================================================================
lo_ftp_configs = []

# Xbox 360 FTP configuration
o_ftp_cfg_xbox360 = ftpextra.FtpConfig()
o_ftp_cfg_xbox360.s_name = 'xbox360'
o_ftp_cfg_xbox360.s_host = '192.168.0.106'
o_ftp_cfg_xbox360.s_user = 'xbox'
o_ftp_cfg_xbox360.s_pwd = 'xbox'
o_ftp_cfg_xbox360.s_root = '/Hdd1/Freestyle Dash/Plugins/UserData'
o_ftp_cfg_xbox360.ls_get_extensions = ('bmp')
o_ftp_cfg_xbox360.ls_del_extensions = ('meta')
o_ftp_cfg_xbox360.b_recursive = True
o_ftp_cfg_xbox360.b_file_keep = True
o_ftp_cfg_xbox360.b_dir_keep = True

lo_ftp_configs.append(o_ftp_cfg_xbox360)


# FTP image gathering
#=======================================================================================================================
for o_ftp_config in lo_ftp_configs:
    o_ftp = ftpextra.Ftp(o_ftp_config)