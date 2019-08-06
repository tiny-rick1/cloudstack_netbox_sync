class VM:
    """
    VM represents a virtual machine
    """
    def __init__(self,vm,config,nb_connection,cs_connection):
        """
        :param vm: dict
        :param config: ConfigParser
        """
        self.nb_connection = nb_connection
        self.cs_connection = cs_connection
        self.config = config
        self.name = vm['displayname']
        self.cs_id = vm['id']
        self.zone = vm['zonename']
        try:
            self.node = vm['hostname']
        except:
            self.node = ''
        self.role = self.config['NETBOX_ID_MAPPING']['role']
        self.status = self.__status(vm['state'])
        self.cluster = self.__cluster(vm['zonename'])
        self.nic = vm['nic']
        self.comments = vm['instancename']
        self.vcpus = vm['cpunumber']
        self.memory = vm['memory']
        self.project = vm['project']
        self.tenant = self.__get_tenants_list()[self.project]
        self.platform = self.config['NETBOX_ID_MAPPING']['platform']
        self.disk = self.__get_total_disk_size(vm['id'],vm['projectid'])
        self.is_imported = self.__check_if_imported()


    def __repr__(self):
        """
        Represent the VM information as dict
        """
        message = ""
        for key, val in self.__create_dict().items():
            message += f"{key} : {val}\n"
        message += f"imported : {self.is_imported}"
        return message

    def __status(self,state):
        """
        Get VM status
        :param state: str
        :return: int
        """
        if state == 'Running':
            return 1
        else:
            return 0

    def __cluster(self,zonename):
        """
        Get Cluster Status
        :param zonename: str
        :return: int
        """
        if zonename == 'Private':
            return self.config['NETBOX_ID_MAPPING']['private']
        else:
            return self.config['NETBOX_ID_MAPPING']['public']

    def __get_total_disk_size(self,vm_id,project_id):
        """
        Method for calculating total disk size
        :param vm_id: str
        :param project_id: str
        :return: int
        """
        size = 0
        for disk in self.cs_connection.listVolumes(listall=True,virtualmachineid=vm_id,projectid=project_id)['volume']:
            size += int(disk['size']/1073741824)
        return size

    def __create_dict(self):
        """
        Method for creating dict to be pased to netbox function
        :return: dict
        """
        return {'name' : self.name,
                'role' : self.role,
                'status': self.status,
                'cluster' : self.cluster,
                'platform' : self.platform,
                'comments' : self.comments,
                'vcpus' : self.vcpus,
                'memory' : self.memory,
                'disk' : self.disk,
                'tenant' : self.tenant
                }

    def __get_tenants_list(self):
        """
        Method for producing dict of netbox tenant to id mapping
        :return: dict
        """
        tenants = dict()
        for tenant in self.nb_connection.tenancy.tenants.all():
            tenants[tenant.name] = tenant.id
        return tenants

    def __check_if_imported(self):
        """
        Method for checking is vm exists in ipam
        :return: bool
        """
        if self.nb_connection.virtualization.virtual_machines.get(name=self.name):
            return True
        else:
            return False

    def __create_vm_in_netbox(self):
        """
        Method creating Virtual Macine item in Netbox
        """
        response = self.nb_connection.virtualization.virtual_machines.create(self.__create_dict())
        self.nb_id = response.id
        self.nb_vm = self.nb_connection.virtualization.virtual_machines.get(response.id)

    def __create_eth(self):
        """
        Method creating network card object in netbox and assigning it to our vm object
        """
        self.eth = self.nb_connection.virtualization.interfaces.create(
            device=0,
            name="eth0",
            form_factor=0,
            enabled=True,
            mac_address=self.nic[0]['macaddress'],
            virtual_machine=self.nb_id
            )

    def __get_eth(self):
        """
        get interface item from netboxsettings
        :return:
        """
        self.eth = self.nb_connection.virtualization.interfaces.get(virtual_machine_id=self.nb_vm.id)

    def __assign_ip_address(self):
        """
        Assign existing IP address
        """
        if self.zone == 'Private':
            self.ip = self.nb_connection.ipam.ip_addresses.get(address=self.nic[0]['ipaddress'] + self.config['NETBOX_ID_MAPPING']['private_mask'])
        else:
            self.ip = self.nb_connection.ipam.ip_addresses.get(address=self.nic[0]['ipaddress'] + self.config['NETBOX_ID_MAPPING']['public_mask'])
        self.ip.interface = self.eth.id
        self.ip.save()

    def __create_ip_address(self):
        """
        Create ne IP address item in netbox
        """
        if self.zone == 'Private':
            self.ip = self.nb_connection.ipam.ip_addresses.create(
                address=self.nic[0]['ipaddress'] + self.config['NETBOX_ID_MAPPING']['private_mask'],
                vfr="null",
                status=1,
                interface=self.eth.id)
        else:
            self.ip = self.nb_connection.ipam.ip_addresses.create(
                address=self.nic[0]['ipaddress'] + self.config['NETBOX_ID_MAPPING']['public_mask'],
                vfr="null",
                status=1,
                interface=self.eth.id)

    def __set_primary_ip(self):
        """
        Sets primary ip4 address
        :return:
        """
        self.nb_vm.primary_ip4 = self.ip.id

    def __set_custom_fields(self):
        """
        Method for setting custom atributes, Need to be individualy adjusted for your setup, mappings set in settings.ini file
        If custom_filed not used may be ommited
        :return:
        """
        #example:
        # if if self.cluster == self.config['NETBOX_ID_MAPPING']['private']:
        #     if self.status:
        #         self.nb_vm.custom_fields['parent'] = self.node
        #         self.nb_vm.custom_fields['icinga import'] = True
        #         try:
        #             if self.project in self.config['MONITORED_PROJECTS']['projects']:
        #                 for key,val in self.config['AGENT_PRIV'].items():
        #                     self.nb_vm.custom_fields[key] = val
        #             else:
        #                 for key,val in self.config['BASIC_PRIV'].items():
        #                     self.nb_vm.custom_fields[key] = val
        #         except:
        #             for key,val in self.config['BASIC_PRIV'].items():
        #                 self.nb_vm.custom_fields[key] = val
        # else:
        #     if self.status:
        #         self.nb_vm.custom_fields['parent'] = self.node
        #         self.nb_vm.custom_fields['icinga import'] = True
        #         try:
        #             if self.project in self.config['MONITORED_PROJECTS']['projects']:
        #                 for key, val in self.config['AGENT_PUB'].items():
        #                     self.nb_vm.custom_fields[key] = val
        #             else:
        #                 for key, val in self.config['BASIC_PUB'].items():
        #                     self.nb_vm.custom_fields[key] = val
        #         except:
        #             for key, val in self.config['BASIC_PUB'].items():
        #                 self.nb_vm.custom_fields[key] = val

    def __update_vm_info(self):
        self.nb_vm.vcpus = self.vcpus
        self.nb_vm.memory = self.memory
        self.nb_vm.disk = self.disk

    def import_to_netbox(self):
        """
        Method kickstaring netbox import
        """
        self.__create_vm_in_netbox()
        self.__create_eth()
        try:
            self.__assign_ip_address()
        except:
            self.__create_ip_address()
        self.__set_primary_ip()
        self.__set_custom_fields()
        self.nb_vm.save()

    def update_in_netbox(self):
        """
        Method for updating existing netbox item
        :param nb_connection: object
        """
        self.nb_vm = self.nb_connection.virtualization.virtual_machines.get(name=self.name)
        if self.status == 1: # 1 - active 2 offline
            self.nb_vm.status = 1
        else:
            self.nb_vm.status = 0
        self.__get_eth()
        try:
            self.__assign_ip_address()
        except:
            self.__create_ip_address()
        self.__set_primary_ip()
        self.__update_vm_info()
        self.nb_vm.save()