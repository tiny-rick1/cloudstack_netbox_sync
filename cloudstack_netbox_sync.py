from cs import CloudStack
import pynetbox
from configparser import ConfigParser
from VM import VM

def netbox_vm_list(nb_connection,config):
    """
    Retrives VM's list from netbox , only vm that are in cloudstack defined clusters
    :param nb_connection: Api
    :param config: ConfigParser
    :return: list
    """
    vm_list = list()
    for vm in nb_connection.virtualization.virtual_machines.all():
        if vm.cluster.id == config['NETBOX_ID_MAPPING']['private'] or vm.cluster.id == config['NETBOX_ID_MAPPING']['public']:
            vm_list.append(vm.name)
    return vm_list


def cloudstack_vm_list(cs_connection):
    """
    Retrives All VM's list from cloudstack excluding default project
    :param cs_connection: CloudStack
    :return: list
    """
    vm_list = list()
    for project in cs_connection.listProjects(listall=True)['project']:
        if project['vmtotal'] > 0:
            for vm in cs_connection.listVirtualMachines(listall=True,projectid=project['id'])['virtualmachine']:
                vm_list.append(vm['displayname'])
    return vm_list


def clean_netbox(cs_connection,nb_connection,config):
    """
    Compares netbox vm list with cloudstack vm list and removes VM's from netbox that are not present in cloudstack
    :param cs_connection: CloudStack
    :param nb_connection: Api
    """
    nb_vm_list = netbox_vm_list(nb_connection,config)
    cs_vm_list = cloudstack_vm_list(cs_connection)
    for vm in nb_vm_list:
        if vm not in cs_vm_list:
            nb_vm = nb_connection.virtualization.virtual_machines.get(name=vm)
            nb_vm.delete()



def main():
    # load settings form settings.ini file
    config = ConfigParser()
    config.read('/usr/local/cloudstack_netbox_sync/settings.ini')
    # Conection to netbox and cloudstack API
    nb_connection = pynetbox.api(config['NETBOX_CONNECTION']['url'],
                                 token=config['NETBOX_CONNECTION']['token'])

    cs_connection = CloudStack(endpoint=config['CLOUDSTACK_CONNECTION']['endpoint'],
                               key=config['CLOUDSTACK_CONNECTION']['key'],
                               secret=config['CLOUDSTACK_CONNECTION']['secret'])
    # Start
    for project in cs_connection.listProjects(listall=True)['project']:
        if project['vmtotal'] > 0:
            for virtualmachine in cs_connection.listVirtualMachines(listall=True,projectid=project['id'])['virtualmachine']:
                machine = VM(virtualmachine,config,nb_connection,cs_connection)
                if not machine.is_imported:
                    print(machine.name)
                    machine.import_to_netbox()
                else:
                    machine.update_in_netbox()

    #Prune removed machines
    clean_netbox(cs_connection,nb_connection)

main()
