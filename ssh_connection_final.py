from ssh_key_file import *
import os

#this function check the HV_version and returns the first octate
def check_hv_version(hostname, password):
    ssh = make_sshConnection(hostname, password)
    stdin, stdout, stderr = ssh.exec_command("cat /etc/redhat-release")
    stdin.close()
    data = stdout.read()
    full_version = str(data.split()[-1])
    hv_version = full_version.split('.')[0]
    ssh.close()
    return hv_version

#function to return the blkid of the shared volume on the OVM3 hypervisor
def get_blkid_ovm3_hypervisor(hostname, password):
    ssh = make_sshConnection(hostname, password)
    stdin, stdout, stderr = ssh.exec_command('blkid -t TYPE=ocfs2 -o value -s UUID /dev/DomUVol/ovmrepo1')
    raw_data = stdout.read()
    # the below line replaces - with nospace
    data = raw_data.replace('-', '')
    # the below Line converts the mixed string to uppercase string
    u_data = data.upper().strip()
    return u_data


#this function makes /OVS/Repositories/*/VirtualDisks directory
def get_dirName(hostname, password):
    u_data = get_blkid_ovm3_hypervisor(hostname, password)
    file_path = os.path.join('/OVS/Repositories/',u_data,'VirtualDisks').replace('\\', '/')
    return file_path

#this function checks makes /OVS/Repositories/*/VirtualMachines directory
def get_dirName_VirtualMachines(hostname, password):
    ssh = make_sshConnection(hostname, password)
    stdin, stdout, stderr = ssh.exec_command('blkid -t TYPE=ocfs2 -o value -s UUID /dev/DomUVol/ovmrepo1')
    raw_data = stdout.read()
    data = raw_data.replace('-', '')
    u_data = data.upper().strip()
    file_path_vmconfig = os.path.join('/OVS/Repositories/',u_data,'VirtualMachines').replace('\\', '/')
    stdin.close()
    ssh.close()
    return file_path_vmconfig


#this function  list of files in /OVS/Repositories/*/VirtualDisks directory
def list_files(hostname, password):
    sftp = make_sftpConnection(hostname, password)
    path = get_dirName(hostname, password)
    file_list = []
    for file in sftp.listdir(path):
        file_list.append(str(file))
    sftp.close()
    return file_list

#this function get the vm names from the Hypervisor
def vm_source(hostname, password):
    ssh = make_sshConnection(hostname, password)
    stdin, stdout, stderr = ssh.exec_command('xm list')
    raw_data1 = stdout.read()
    lines = raw_data1.splitlines()
    vm_names = []
    for line in lines[1:]:
        columns = line.split()
        # vm_names = columns[0]
        vm_names.append(columns[0])
    stdin.close()
    ssh.close()
    return vm_names

#this function shutsdown the VM form Virtual Machine
def shutdown_func(hostname, password):
    ssh = make_sshConnection(hostname, password)
    stdin, stdout, stderr = ssh.exec_command('shutdown -h now')
    stdin.close()
    ssh.close()

#this function shutsdown the VM from Hyepervisor
def shutdown_vm_from_hypervisor(hvname, vmname, password):
    ssh = make_sshConnection(hvname, password)
    stdin, stdout, stderr = ssh.exec_command('xm shutdown %s' % vmname)
    stdin.close()
    ssh.close()
    return True

#this function builds source and destination paths to copy img files, used only OVM3 to OVM3
def scp_from_sourcehv(shvname, dhvname, vmname, password):
    ssh = make_sshConnection(shvname, password)
    make_source_shared_dir(shvname, password)
    id_file = '/tmp/ssh_key/id_rsa'
    elem1 = vmname
    elem2 = '_root.img'
    file_name = ''.join([elem1, elem2])
    s_path = get_dirName(shvname, password)
    s_complete_path = '/'.join([s_path,file_name])
    # s_complete_path = '/OVS/Repositories/B423AFB039394B179AD28186B92888C8/VirtualDisks/test1.img'
    d_path = get_dirName(dhvname, password)
    print "Path for VM image file in the Source Hypervisor", s_complete_path
    print "Path for Destination Hypervisor", d_path
    # write scp code
    stdin, stdout, stderr = ssh.exec_command(
        'scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s root@%s:%s ' % (
        id_file, s_complete_path, dhvname, d_path))
    exit_code = stdout.channel.recv_exit_status()
    stdin.close()
    ssh.close()
    if exit_code == 0:
        return 0
    else:
        return 1

# this code copies the tar file which contains the VM config and XML file
def scp_vm_cfg_file_from_sourcehv(shvname,dhvname,vmname,password):
    ssh = make_sshConnection(shvname, password)
    make_source_shared_dir(shvname, password)
    dest_hv_path_for_config_file(dhvname,vmname, password)
    id_file = '/tmp/ssh_key/id_rsa'
    elem1 = vmname
    path = get_dirName_VirtualMachines(shvname, password)
    elem2 = '*'
    s_path = '/'.join([path,elem1])
    source_path = '/'.join([s_path,elem2])
    path_1 = get_dirName_VirtualMachines(dhvname, password)
    d_path = '/'.join([path_1,elem1])
    print "Full path of tar file which conatins .cfg file and .xml file", source_path
    print "Full path of destination Hypervisor for copying cfg and .xml file", d_path
    stdin, stdout, stderr = ssh.exec_command(
        'scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s root@%s:%s ' % (
        id_file, source_path, dhvname, d_path))
    exit_code = stdout.channel.recv_exit_status()
    stdin.close()
    ssh.close()
    if exit_code == 0:
        return 0
    else:
        return 1

# this function makes the dir under virtual machines with VM name
def dest_hv_path_for_config_file(hostname,vmname,password):
    ssh = make_sshConnection(hostname, password)
    path1 = get_dirName_VirtualMachines(hostname, password)
    stdin, stdout, stderr = ssh.exec_command('cd %s; mkdir %s' %(path1, vmname))
    stdin.close()
    ssh.close()

#this function changes the blkid on config file of a vm.cfg file
def change_the_blkid_vm_config_file(shvname,dhvname,vmname,password):
    src_blkid = get_blkid_ovm3_hypervisor(shvname, password)
    dest_blkid = get_blkid_ovm3_hypervisor(dhvname,password)
    print "source blkid is", src_blkid
    print "destination blkid is", dest_blkid
    ssh = make_sshConnection(dhvname, password)
    sftp_client = ssh.open_sftp()
    elem1 = vmname
    elem2 = 'vm.cfg'
    path_1 = get_dirName_VirtualMachines(dhvname, password)
    d_path = '/'.join([path_1, elem1])
    d_path_config = '/'.join([d_path, elem2])
    print "path of vm.cfg file in destination HV", d_path_config
    try:
        with sftp_client.open(d_path_config, 'r') as f:
            newlines = []
            for line in f.readlines():
                newlines.append(line.replace(src_blkid, dest_blkid))
        with sftp_client.open(d_path_config, 'w') as f:
            for line in newlines:
                f.write(line)
    finally:
        sftp_client.close()
    ssh.close()


#this function finds the free space on the volume group on a remote hypervisor
def find_freesize_vg(hostname, password):
    ssh = make_sshConnection(hostname, password)
    stdin, stdout, stderr = ssh.exec_command('vgdisplay | grep -i Free')
    rawdata = stdout.read()
    data1 = str(rawdata.splitlines())
    data2 = data1.split('/')
    free_pp_count = int(data2[1].split()[1])
    free_vg_size = (32 * free_pp_count) / 1024
    stdin.close()
    ssh.close()
    return free_vg_size


# write a function to get the size of a LV on a source HV
def get_the_size_of_lv(shvname,vmname, password):
    ssh = make_sshConnection(shvname, password)
    elem1 = '/dev/DomUVol'
    elem2 = vmname
    lv_name = '/'.join([elem1, elem2])
    stdin, stdout, stderr = ssh.exec_command('lvdisplay %s | grep -i size' % lv_name)
    rawdata = stdout.read().split()
    size = int(float(rawdata[2]))
    return size


# this function creates a logical volume on a remote hypervisor
def create_lv_on_dest_hypervisor(shvname,dhvname,vmname,password):
    ssh = make_sshConnection(dhvname, password)
    vg_free_space = find_freesize_vg(dhvname, password)
    lv_size = get_the_size_of_lv(shvname,vmname, password)
    elem1 = 'G'
    lvsize_gb = ''.join([str(lv_size), elem1])
    if vg_free_space >= lv_size:
        print "creating the LV"
        stdin, stdout, stderr = ssh.exec_command('lvcreate -L %s DomUVol --name %s' % (lvsize_gb, vmname))
        exit_code = stdout.channel.recv_exit_status()
        stdin.close()
    else:
        print "no free space on the hypervisor"
    ssh.close()
    if exit_code == 0:
        return 0
    else:
        return 1

#this function copies the logical Volume from source to destination
def disk_transfer_using_dd_command(shvname,dhvname,vmname,password):
    ssh = make_sshConnection(shvname,password)
    make_source_shared_dir(shvname,password)
    id_file = '/tmp/ssh_key/id_rsa'
    elem1 = vmname
    elem2 = '/dev/DomUVol'
    lv_name = '/'.join([elem2,elem1])
    # stdin, stdout, stderr = ssh.exec_command('dd bs=8M if=/dev/DomUVol/slc14rcr | ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i /tmp/ssh_key/id_rsa slcal654 dd bs=8M of=/dev/DomUVol/slc14rcr')
    stdin, stdout, stderr = ssh.exec_command(
        'dd bs=64M if=%s | ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s dd bs=64M of=%s' % ( lv_name, id_file, dhvname, lv_name))
    # print (stderr.readlines())
    exit_code = stdout.channel.recv_exit_status()
    stdin.close()
    ssh.close()
    if exit_code == 0:
        return 0
    else:
        return 1

# this function is to transfer the configuration file from OVM 2 hypervisor
def scp_config_file_from_ovm2_hv(shvname,dhvname,vmname,password):
    ssh = make_sshConnection(shvname, password)
    make_source_shared_dir(shvname, password)
    elem1 = vmname
    elem2 = 'domU_'
    path = '/etc/xen/domU'
    config_file = ''.join([elem2,elem1])
    s_path = '/'.join([path,config_file])
    id_file = '/tmp/ssh_key/id_rsa'
    print "source path is ", s_path
    print "destination path ", path
    stdin, stdout, stderr = ssh.exec_command(
        'scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s root@%s:%s ' % (
            id_file, s_path, dhvname, path))
    exit_code = stdout.channel.recv_exit_status()
    stdin.close()
    ssh.close()
    if exit_code == 0:
        return 0
    else:
        return 1

#this function transfers the logical Volume from OVM2 HV to OVM3 HV by copying it to img format
def disk_transfer_from_ovm2_ovm3(shvname,dhvname,vmname,password):
    ssh = make_sshConnection(shvname, password)
    make_source_shared_dir(shvname, password)
    id_file = '/tmp/ssh_key/id_rsa'
    elem1 = vmname
    elem2 = '/dev/DomUVol'
    elem3 = '_root.img'
    lv_name = '/'.join([elem2, elem1])
    img_file = ''.join([elem1,elem3])
    d_path = get_dirName(dhvname, password)
    dest_comp_path = '/'.join([d_path,img_file])
    print "logical Volume to be copied", lv_name
    print "Destination path where the LV be copied", dest_comp_path
    stdin, stdout, stderr = ssh.exec_command(
        'dd bs=64M if=%s | ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s dd bs=64M of=%s' % (
        lv_name, id_file, dhvname, dest_comp_path))
    # print (stderr.readlines())
    exit_code = stdout.channel.recv_exit_status()
    stdin.close()
    ssh.close()
    if exit_code == 0:
        return 0
    else:
        return 1

#this function transfers the configuration file to OVM2 HV to OVM3 HV
def transfer_config_file_ovm2_ovm3(shvname,dhvname,vmname,password):
    ssh = make_sshConnection(shvname, password)
    make_source_shared_dir(shvname, password)
    elem1 = vmname
    elem2 = 'domU_'
    path = '/etc/xen/domU'
    config_file = ''.join([elem2, elem1])
    s_path = '/'.join([path, config_file])
    id_file = '/tmp/ssh_key/id_rsa'
    dest_hv_path_for_config_file(dhvname, vmname, password)
    path1 = get_dirName_VirtualMachines(dhvname, password)
    elem3 = 'vm.cfg'
    d_path = '/'.join([path1,elem1])
    d_config_path = '/'.join([d_path,elem3])
    print "source path is ", s_path
    print "destination path ", d_config_path
    stdin, stdout, stderr = ssh.exec_command(
        'scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s root@%s:%s ' % (
            id_file, s_path, dhvname, d_config_path))
    exit_code = stdout.channel.recv_exit_status()
    stdin.close()
    ssh.close()
    if exit_code == 0:
        return 0
    else:
        return 1

#this function replaces phy: to file: in OVM3 config file
def replace_phy_file_vm_config_file(dhvname,vmname,password):
    elem1 = 'phy:'
    elem2 = '/dev/DomUVol'
    elem3 = vmname
    lv_name = '/'.join([elem2,elem3])
    string_1 = ''.join([elem1,lv_name])
    elem4 = '_root.img'
    file_name = ''.join([elem3, elem4])
    d_path = get_dirName(dhvname, password)
    d_complete_path = '/'.join([d_path, file_name])
    elem4 = 'file:'
    string_2 = ''.join([elem4,d_complete_path])
    print "string to be replaced", string_1
    print "changed string", string_2
    ssh = make_sshConnection(dhvname, password)
    sftp_client = ssh.open_sftp()
    elem1 = vmname
    elem2 = 'vm.cfg'
    path_1 = get_dirName_VirtualMachines(dhvname, password)
    d_path = '/'.join([path_1, elem1])
    d_path_config = '/'.join([d_path, elem2])
    print "path of vm.cfg file in destination HV", d_path_config
    try:
        with sftp_client.open(d_path_config, 'r') as f:
            newlines = []
            for line in f.readlines():
                newlines.append(line.replace(string_1, string_2))
        with sftp_client.open(d_path_config, 'w') as f:
            for line in newlines:
                f.write(line)
    finally:
        sftp_client.close()
    ssh.close()

#this function is to create a soft link to the configuration file
def create_soft_link_configfile(dhvname,vmname, password):
    ssh = make_sshConnection(dhvname, password)
    elem1 = vmname
    elem2 = 'domU_'
    path = '/etc/xen/domU'
    config_file = ''.join([elem2, elem1])
    s_config_file_path = '/'.join([path, config_file])
    path1 = '/etc/xen/auto'
    dest_config_file_path = '/'.join([path1,config_file])
    stdin, stdout, stderr = ssh.exec_command('ln -s %s %s' %(s_config_file_path, dest_config_file_path))
    stdin.close()
    ssh.close()

#this function creates a softlink on ovm 3 hypervisor for ovm2 -3 tranfer module
def create_soft_link_configfile_ovm_3(dhvname,vmname, password):
    ssh = make_sshConnection(dhvname, password)
    elem1 = vmname
    elem2 = 'vm.cfg'
    path_1 = get_dirName_VirtualMachines(dhvname, password)
    d_path = '/'.join([path_1, elem1])
    s_config_file_path = '/'.join([d_path, elem2])
    path1 = '/etc/xen/auto'
    dest_config_file_path = '/'.join([path1,elem1])
    stdin, stdout, stderr = ssh.exec_command('ln -s %s %s' %(s_config_file_path, dest_config_file_path))
    stdin.close()
    ssh.close()

#this function gets the size in GB of a image file on OV3 hypervisor
def find_the_size_of_imagefile(shvname,vmname,password):
    ssh = make_sshConnection(shvname, password)
    elem1 = vmname
    elem2 = '_root.img'
    file_name = ''.join([elem1, elem2])
    s_path = get_dirName(shvname, password)
    s_complete_path = '/'.join([s_path, file_name])
    # s_complete_path = '/OVS/Repositories/B423AFB039394B179AD28186B92888C8/VirtualDisks/test1.img'
    print "Path for VM image file in the Source Hypervisor", s_complete_path
    stdin, stdout, stderr = ssh.exec_command('ls -lh %s' % s_complete_path)
    rawdata = stdout.read()
    data1 = str(rawdata.splitlines())
    data2 = data1.split(' ')
    size = int(float(data2[4][:-1]))
    stdin.close()
    ssh.close()
    return size

# this function creates a LV on OVM2 HV for OVM3-2 transfer
def create_lv_on_destination_hv_ovm3to2(shvname,dhvname,vmname, password):
    ssh = make_sshConnection(dhvname, password)
    vg_free_space = find_freesize_vg(dhvname, password)
    lvsize = find_the_size_of_imagefile(shvname,vmname,password)
    elem1 = 'G'
    lvsize_gb = ''.join([str(lvsize),elem1])
    print "size of lv need to be created", lvsize_gb
    if vg_free_space >= lvsize:
        print "creating the LV"
        stdin, stdout, stderr = ssh.exec_command('lvcreate -L %s DomUVol --name %s' % (lvsize_gb, vmname))
        exit_code = stdout.channel.recv_exit_status()
        stdin.close()
    else:
        print "no free space on the hypervisor"
    ssh.close()
    if exit_code == 0:
        return 0
    else:
        return 1

#this function will dd the img file to lv on the destination HV
def disk_transfer_from_ovm3_ovm2(shvname,dhvname,vmname,password):
    ssh = make_sshConnection(shvname, password)
    make_source_shared_dir(shvname, password)
    id_file = '/tmp/ssh_key/id_rsa'
    elem1 = vmname
    elem2 = '_root.img'
    img_file = ''.join([elem1, elem2])
    s_path = get_dirName(shvname, password)
    src_comp_path = '/'.join([s_path,img_file])
    elem3 = '/dev/DomUVol'
    lv_name = '/'.join([elem3, elem1])
    print "Image path to be copied", src_comp_path
    print "Destination path where the LV be copied", lv_name
    stdin, stdout, stderr = ssh.exec_command(
        'dd bs=64M if=%s | ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s dd bs=64M of=%s' % (
        src_comp_path, id_file, dhvname, lv_name))
    # print (stderr.readlines())
    exit_code = stdout.channel.recv_exit_status()
    stdin.close()
    ssh.close()
    if exit_code == 0:
        return 0
    else:
        return 1

#this function is to transfer config file from ovm3 to 2
def transfer_config_file_ovm3_ovm2(shvname,dhvname,vmname,password):
    ssh = make_sshConnection(shvname, password)
    make_source_shared_dir(shvname, password)
    id_file = '/tmp/ssh_key/id_rsa'
    path1 = get_dirName_VirtualMachines(shvname, password)
    elem1 = vmname
    elem2 = 'vm.cfg'
    s_path = '/'.join([path1, elem1])
    s_config_path = '/'.join([s_path,elem2])
    elem3 = 'domU_'
    d_path = '/etc/xen/domU'
    d_config_file = ''.join([elem3,elem1])
    d_config_file_path = '/'.join([d_path,d_config_file])
    # config_file = ''.join([elem2, elem1])
    # s_path = '/'.join([path, config_file])
    print "source path is ", s_config_path
    print "destination path ", d_config_file_path
    stdin, stdout, stderr = ssh.exec_command(
        'scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s root@%s:%s ' % (
            id_file, s_config_path, dhvname, d_config_file_path))
    exit_code = stdout.channel.recv_exit_status()
    stdin.close()
    ssh.close()
    if exit_code == 0:
        return 0
    else:
        return 1

# this code changes the disk string from file to phy
def replace_file_phy_vm_config_file(shvname,dhvname,vmname,password):
    elem1 = 'phy:'
    elem2 = '/dev/DomUVol'
    elem3 = vmname
    lv_name = '/'.join([elem2,elem3])
    string_1 = ''.join([elem1,lv_name])
    elem4 = '_root.img'
    file_name = ''.join([elem3, elem4])
    d_path = get_dirName(shvname, password)
    d_complete_path = '/'.join([d_path, file_name])
    elem4 = 'file:'
    string_2 = ''.join([elem4,d_complete_path])
    print "string to be replaced", string_2
    print "changed string", string_1
    ssh = make_sshConnection(dhvname, password)
    sftp_client = ssh.open_sftp()
    elem1 = vmname
    elem2 = 'domU_'
    path = '/etc/xen/domU'
    config_file = ''.join([elem2, elem1])
    d_path_config = '/'.join([path,config_file])
    print "path of vm.cfg file in destination HV", d_path_config
    try:
        with sftp_client.open(d_path_config, 'r') as f:
            newlines = []
            for line in f.readlines():
                newlines.append(line.replace(string_2, string_1))
        with sftp_client.open(d_path_config, 'w') as f:
            for line in newlines:
                f.write(line)
    finally:
        sftp_client.close()
    ssh.close()

# this function starts the VM on destination HV
def start_vm_on_ovm2_hv(dhvname,vmname, password):
    ssh = make_sshConnection(dhvname, password)
    elem1 = vmname
    elem2 = 'domU_'
    path = '/etc/xen/auto'
    vm_config_file = ''.join([elem2,elem1])
    stdin, stdout, stderr = ssh.exec_command('cd %s; xm cr %s' % (path, vm_config_file))
    stdin.close()
    ssh.close()
#this function starts the vm from HV
def start_vm_on_ovm3_hv(dhvname,vmname, password):
    ssh = make_sshConnection(dhvname, password)
    path = '/etc/xen/auto'
    stdin, stdout, stderr = ssh.exec_command('cd %s; xm cr %s' % (path, vmname))
    stdin.close()
    ssh.close()

#this function is to make the ping test of the VM
def ping_check(hostname):
    response = os.system("ping -n 1 " + hostname)
     # and then check the response...
    if response == 0:
       return 0
    else:
        return 1
#this function renames the LV on source HV
def rename_lv_source_HV(shvname,vmname, password):
    ssh = make_sshConnection(shvname, password)
    elem1 = vmname
    elem2 = '/dev/DomUVol'
    lv_name = '/'.join([elem2,elem1])
    elem3 = '_migrated'
    lv_name1 = ''.join([lv_name,elem3])
    stdin, stdout, stderr = ssh.exec_command('lvrename %s %s' % (lv_name, lv_name1))
    stdin.close()
    ssh.close()
#this function re-names the vm config file on OVM2 Source HV
def rename_config_file_ovm2_source_HV(shvname,vmname, password):
    ssh = make_sshConnection(shvname, password)
    elem1 = vmname
    elem2 = 'domU_'
    elem3 = '_migrated'
    path = '/etc/xen/domU'
    file = ''.join([elem2,elem1])
    config_file1 = '/'.join([path,file])
    config_file2 = ''.join([config_file1,elem3])
    stdin, stdout, stderr = ssh.exec_command('mv %s %s' % (config_file1, config_file2))
    stdin.close()
    ssh.close()
#this function renames the image file on source HV
def rename_image_file_source_HV(shvname,vmname, password):
    ssh = make_sshConnection(shvname, password)
    elem1 = vmname
    elem2 = '_root.img'
    elem3 = '_migrated'
    img_file = ''.join([elem1, elem2])
    s_path = get_dirName(shvname, password)
    src_comp_path = '/'.join([s_path, img_file])
    src_comp_path1 = ''.join([src_comp_path,elem3])
    stdin, stdout, stderr = ssh.exec_command('mv %s %s' % (src_comp_path, src_comp_path1))
    stdin.close()
    ssh.close()
#this function renames the config file on ovm3 HV
def rename_config_file_ovm3_source_HV(shvname,vmname, password):
    ssh = make_sshConnection(shvname, password)
    elem1 = vmname
    elem2 = 'vm.cfg'
    elem3 = '_migrated'
    path_1 = get_dirName_VirtualMachines(shvname, password)
    d_path = '/'.join([path_1, elem1])
    s_config_file_path = '/'.join([d_path, elem2])
    s_config_file_path1 = ''.join([s_config_file_path,elem3])
    stdin, stdout, stderr = ssh.exec_command('mv %s %s' % (s_config_file_path, s_config_file_path1))
    stdin.close()
    ssh.close()
