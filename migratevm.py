import argparse
import os
import paramiko
from devops_valid import check_devops_status
import getpass
# from wallet import Wallet
from ssh_connection8 import *
import time

#function for parsing Arguments

class InvalidToken(Exception):
    pass

def parse_args():

    parser = argparse.ArgumentParser()
    # parser.add_argument('-vm', '--vms', help='delimited list input of VM names', type=str, required=True)
    parser.add_argument('-vm', '--vms', help='VM Names (only one)', required=True)
    parser.add_argument('-s', '--shv', help='Source Hypervisor Name', required=True)
    parser.add_argument('-d', '--dhv', help='Destination Hypervisor Name',required=True)
    args = parser.parse_args()
    # args.vms = args.vms.split(',')
    return args


def main():

    args = parse_args()
    password = getpass.getpass()
    vms = check_devops_status(args.vms)
    shv = check_devops_status(args.shv)
    dhv = check_devops_status(args.dhv)
    if shv and dhv:
        for i in range(2):
            if i == 1:
                shv_version = check_hv_version(args.shv, password)
            else:
                dhv_version = check_hv_version(args.dhv, password)

        print ("SHV and DHV are both hv")
        print "Source Hypervisor Version:", shv_version
        print "Destination Hypervisor: ", dhv_version

#Below if statement executes the code for  OVM2 to OVM2 migration
        if str(shv_version) == '2' and str(dhv_version) == '2':
            print ("Executing OVM2-OVM2 Module")
            if args.vms in vm_source(args.shv, password):
                print ("VM exists in source hypervisor and shutting down the VM now")
                shutdown_vm_from_hypervisor(args.shv, args.vms, password)
                time.sleep(15)
                if ping_check(args.vms) == 1:
                    print ("VM is down and we can Initiate the img file transfer")
                    print ("Create a LV in a destination machine")
                    create_lv_on_dest_hypervisor(args.shv,args.dhv, args.vms, password)
                    #we need to write an exit code if LV is not created also let the user know the lv created
                    if disk_transfer_using_dd_command(args.shv,args.dhv,args.vms, password) == 0:
                        print ("DD of the volume is successful")
                    else:
                        print ("DD of the volume is failed")
                    if scp_config_file_from_ovm2_hv(args.shv,args.dhv,args.vms, password) == 0:
                        print ("Configuration file is transferred ")
                        create_soft_link_configfile(args.dhv,args.vms, password)
                        start_vm_on_ovm2_hv(args.dhv,args.vms, password)
                    else:
                        print ("Configuration file transfer failed")
                else:
                    print (" VM is not down and you should exit from the script")
            else:
                print ("VM is not present in source Hypervisor")

#Below if statement executes the code for OVM2 to OVM3 Migration
        elif str(shv_version) == '2' and str(dhv_version) == '3':
            print ("Executing OVM2-OVM3 Module")
            if args.vms in vm_source(args.shv, password):
                print ("VM exists in source hypervisor and shutting down the VM now")
                shutdown_vm_from_hypervisor(args.shv, args.vms, password)
                time.sleep(15)
                if ping_check(args.vms) == 1:
                    print ("VM is down and we can Initiate the img file transfer")
                    if disk_transfer_from_ovm2_ovm3(args.shv,args.dhv,args.vms,password) == 0:
                        print ("DD of the volume is successful")
                    else:
                        print ("DD of the volume is failed")
                    if transfer_config_file_ovm2_ovm3(args.shv,args.dhv,args.vms,password) == 0:
                        print ("Configuration file is transferred ")
                        replace_phy_file_vm_config_file(args.dhv,args.vms,password)
                        create_soft_link_configfile_ovm_3(args.dhv,args.vms, password)
                        start_vm_on_ovm3_hv(args.dhv,args.vms, password)
                    else:
                        print ("Configuration file transfer failed")
                else:
                    print (" VM is not down and you should exit from the script")
            else:
                print ("VM is not present in source Hypervisor")
# below if statement executs the code for OVM3 to OVM2 migration
        elif str(shv_version) == '3' and str(dhv_version) == '2':
            print ("Executing OVM3-OVM2 Module")
            if args.vms in vm_source(args.shv, password):
                print ("VM exists in source hypervisor and shutting down the VM now")
                shutdown_vm_from_hypervisor(args.shv, args.vms, password)
                time.sleep(15)
                if ping_check(args.vms) == 1:
                    print ("VM is down and we can Initiate the img file transfer")
                    create_lv_on_destination_hv_ovm3to2(args.shv,args.dhv,args.vms, password)
                    print ("lv created")
                    if disk_transfer_from_ovm3_ovm2(args.shv,args.dhv,args.vms,password) == 0:
                        print ("DD of the volume is successful")
                    else:
                        print ("DD of the volume is failed")
                    if transfer_config_file_ovm3_ovm2(args.shv,args.dhv,args.vms, password) == 0:
                        print ("Configuration file is transferred ")
                        replace_file_phy_vm_config_file(args.shv,args.dhv,args.vms, password)
                        create_soft_link_configfile(args.dhv, args.vms, password)
                        start_vm_on_ovm2_hv(args.dhv,args.vms,password)
                    else:
                        print ("Configuration file transfer failed")
                else:
                    print ("VM is not down and you should exit from the script")
            else:
                print ("VM is not present in source Hypervisor")

#below if statemen executes the code for OVM3 to OVM3 migration
        elif str(shv_version) == '3' and str(dhv_version) == '3':
            print ("Executing OVM3-OVM3 Module")

            if args.vms in vm_source(args.shv, password):
                print ("VM exists in source hypervisor and shutting down the VM now")
                shutdown_vm_from_hypervisor(args.shv, args.vms, password)
                time.sleep(15)
                if ping_check(args.vms) == 1:
                    print ("VM is down and we can Initiate the img file transfer")
                    print ("Below are the source path and destination path")
                    if scp_from_sourcehv(args.shv,args.dhv,args.vms, password) == 0:
                        print ("Image file copy to the Destination Hypervisor is successful")
                    else:
                        print ("Image file copy failed ")
                    if scp_vm_cfg_file_from_sourcehv(args.shv,args.dhv,args.vms,password) == 0:
                        change_the_blkid_vm_config_file(args.shv,args.dhv,args.vms, password)
                        # untar_vm_config_file function untars the file in destination HV to get the vm config file and xml file
                        print ("Configuration file and XMl file copied to Destination Hypervisor is Successful ")
                        create_soft_link_configfile_ovm_3(args.dhv, args.vms, password)
                        start_vm_on_ovm3_hv(args.dhv, args.vms, password)
                    else:
                        print ("config file transfer failed")

                else:
                    print (" VM is not down and you should exit from the script")

                # shutdown_func(args.vms)
            else:
                print ("VM is not present in source Hypervisor")
    else:
        print ("SHV or DHV is not hv")

if __name__ == '__main__':
    main()