# migrate_vm_ovm_to_ovm
Moving vm from hypervisor to hyeprvisor
# python migratevm.py -vm slc14rcw -s slcal654 -d slcal653
Password:   //supply the root password
Source and Destination are both hypervisors 
Source Hypervisor Version: 2
Destination Hypervisor:  2
Executing OVM2-OVM2 Module
VM exists in source hypervisor and shutting down the VM now
connect: Invalid argument
VM is down and we can Initiate the img file transfer
Create a LV in a destination machine
creating the LV
LV created on Destination Hypervisor
DD of the volume is successful
source path is  /etc/xen/domU/domU_slc14rcw
destination path  /etc/xen/domU
Configuration file is transferred
migration completed
