import paramiko
import os

def make_sshConnection(hostname, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username='root', password=password)
    return ssh

def make_sftpConnection(hostname, password):
    t = paramiko.Transport((hostname, 22))
    t.connect(username='root', password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    return sftp

