import paramiko

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

# this function calls checks if a shared dir already exixts , if not it creates one by calling make_shared_dir
def make_source_shared_dir(hostname, password):
    ssh = make_sshConnection(hostname, password)
    path = '/tmp/ssh_key'
    stdin, stdout, stderr = ssh.exec_command('mount -v')
    raw_data1 = stdout.read()
    lines = raw_data1.splitlines()
    list_path = []
    for line in lines:
        columns = line.split()
        list_path.append(columns[2])
    if path not in list_path:
        make_shared_dir(hostname, password)
        mount_the_key_share(hostname, password)
    stdin.close()
    ssh.close()

#this function creates and mounts a central storage to copy id_rsa file
def make_shared_dir(hostname, password):
    ssh = make_sshConnection(hostname, password)
    stdin, stdout, stderr = ssh.exec_command('mkdir -p /tmp/ssh_key')
    stdin.close()
    ssh.close()

def mount_the_key_share(hostname, password):
    ssh = make_sshConnection(hostname, password)
    stdin, stdout, stderr = ssh.exec_command('mount adcnas402:/export/writeable/ssh_key /tmp/ssh_key')
    stdin.close()
    ssh.close()

#this function unmounts the /mnt/ssh_key dir
def umount_shared_dir(hostname, password):
    ssh = make_sshConnection(hostname, password)
    stdin, stdout, stderr = ssh.exec_command('umount /tmp/ssh_key')
    stdin.close()
    ssh.close()




