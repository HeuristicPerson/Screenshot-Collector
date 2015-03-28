import smbclient

o_smb = smbclient.SambaClient(server="192.168.0.107", share="Emulation", username='mc', password='mc', domain='')

#print o_smb.listdir("/")

if o_smb.exists('gb'):
    print 'YEAHHH'
