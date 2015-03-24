import os
import smbc


def auth_fn(server, share, workgroup, username, password):
    return ('', 'mc', 'mc')


u_samba_address = u'smb://mc/Emulation/user_data/david/gb/screenshots'

o_smb = smbc.Context()
o_smb.optionNoAutoAnonymousLogin = True
o_smb.functionAuthData = auth_fn

try:
    print o_smb.stat(u_samba_address)
except ValueError:
    print 'SMB doesn\'t exist'  # Error when the samba address doesn't exist
except smbc.NoEntryError:
    print 'SMB doesn\'t exist'  # Error when the samba address doesn't exist
except smbc.PermissionError:
    print 'Wrong access data'   # Error when the access data is wrong.

o_smb_dir = o_smb.opendir(u_samba_address)
for o_element in o_smb_dir.getdents():
    print o_element.smbc_type, o_element.name
