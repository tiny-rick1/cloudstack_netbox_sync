# cloudstack_netbox_sync
Script for synchronizing cloudstack virtual machines to netbox via REST api.

## Workflow
1. Read settings file `settings.ini`
2. Create connections to netbox and Cloudstack API's
3. Script iterates through every Cloudstack virtual machine in every project except `default`
4. for every virtual machine from cloudstack VM object is created
5. VM object value `is_ipmorted`is check, if `False` fails virtual machine is imported to netbox, if `True` update is performed.
6. When loop is ended cleanup is performed, removin virtual machines from netbox that are no longer present in Cloudstack.

## Comments
This script uses `settings.ini` file to get mapping of netbox items to their id. Id's in netbox are created when objects are created, so if you intend to use this script you have to retrive them, the easyiest way is to use netbox API browser https://your.netbox.host/api/docs. If you are planing on using `custom_filed` please check VM private method `__set_custom_fields`

## Install
CentoOS7 only

```bash
git clone https://github.com/tiny-rick1/cloudstack_netbox_sync.git
cd cloudstack_netbox_sync
sudo bash install.sh
```

## ToDo
* add logging
* add support for command line parameters
