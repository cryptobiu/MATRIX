import json
import time
from random import shuffle

from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from msrestazure.azure_exceptions import CloudError

from Deployment.deploy import DeployCP


class AzureCP(DeployCP):
    def __init__(self, protocol_config):
        super(AzureCP, self).__init__(protocol_config)
        self.resource_group = 'MatrixRG'

        # init credentials
        with open('GlobalConfigurations/tokens.json', 'r') as cred_files:
            data = json.load(cred_files)
            client_id = data['Azure']['client']
            secret = data['Azure']['secret']
            tenant = data['Azure']['tenant']
            self.subscription_id = data['Azure']['subscription']

        self.credentials = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant)
        self.compute_client = ComputeManagementClient(self.credentials, self.subscription_id)
        self.resource_client = ResourceManagementClient(self.credentials, self.subscription_id)
        self.network_client = NetworkManagementClient(self.credentials, self.subscription_id)

        self.resource_client.providers.register('Microsoft.Compute')
        self.resource_client.providers.register('Microsoft.Network')

        self.public_ips = []
        self.private_ips = []

    def create_key_pair(self):
        raise NotImplementedError

    def create_security_group(self):
        raise NotImplementedError

    @staticmethod
    def check_latest_price(instance_type, region):
        raise NotImplementedError

    def create_availability_set(self, location, protocol_name):
        """
        Creates availability set for the instances
        :param location:
        :param protocol_name:
        :return:
        """
        avset_params = {
            'location': location,
            'sku': {'name': 'Aligned'},
            'platform_fault_domain_count': 3
        }
        try:
            self.compute_client.availability_sets.create_or_update(self.resource_group, '%sAVSet' % protocol_name,
                                                                   avset_params)
            av_set_id = self.compute_client.availability_sets.get(self.resource_group, '%sAVSet' % protocol_name).id
            return av_set_id
        except CloudError as e:
            print('Error while creating availability_set', e.message)

    def create_public_ip_address(self, location, protocol_name):
        """
        Creates public ip for each instance
        :param location:
        :param protocol_name:
        :return: success of the request
        """
        public_ip_addess_params = {
            'location': location,
            'public_ip_allocation_method': 'Dynamic'
        }
        try:
            creation_result = self.network_client.public_ip_addresses.create_or_update(self.resource_group, '%s_IP'
                                                                                       % protocol_name,
                                                                                       public_ip_addess_params)
            return creation_result.result()

        except CloudError as e:
            print('Error while creating availability_set', e.message)

    def create_vnet(self, location, protocol_name):
        vnet_params = {
            'location': location,
            'address_space': {
                'address_prefixes': ['10.0.0.0/16']
            }
        }
        try:
            creation_result = self.network_client.virtual_networks.create_or_update(
                self.resource_group,
                '%sVNet' % protocol_name,
                vnet_params
            )
            return creation_result.result()

        except CloudError as e:
            print('Error while creating availability_set', e.message)

    def create_subnet(self, protocol_name):
        subnet_params = {
            'address_prefix': '10.0.0.0/24'
        }
        try:
            creation_result = self.network_client.subnets.create_or_update(
                self.resource_group,
                '%sVNet' % protocol_name,
                '%sSubnet' % protocol_name,
                subnet_params
            )

            return creation_result.result()
        except CloudError as e:
            print('Error while creating availability_set', e.message)

    def create_nic(self, location, protocol_name, ip_name):
        try:
            subnet_info = self.network_client.subnets.get(
                self.resource_group,
                '%sVNet' % protocol_name,
                '%sSubnet' % protocol_name,
            )
            public_ip_address = self.network_client.public_ip_addresses.get(
                self.resource_group,
                ip_name
            )
            nic_params = {
                'location': location,
                'ip_configurations': [{
                    'name': ip_name,
                    'public_ip_address': public_ip_address,
                    'subnet': {
                        'id': subnet_info.id
                    }
                }]
            }
            creation_result = self.network_client.network_interfaces.create_or_update(
                self.resource_group,
                '%s_Nic' % ip_name[:-3],
                nic_params
            )

            return creation_result.result()

        except CloudError as e:
            print('Error while creating availability_set', e.message)

    def deploy_instances(self):

        with open('GlobalConfigurations/azureRegions.json', 'r') as gc:
            data = json.load(gc)
            key_data = data['eastus']['keyData']

        regions = self.protocol_config['CloudProviders']['azure']['regions']
        machine_type = self.protocol_config['CloudProviders']['azure']['instanceType']
        protocol_name = self.protocol_config['protocol']
        number_of_parties = self.protocol_config['CloudProviders']['azure']['numOfParties']
        number_duplicated_servers = 0

        if len(regions) > 1:
            number_of_instances = number_of_parties // len(regions)
            if number_of_parties % len(regions):
                number_duplicated_servers = number_of_parties % len(regions)
        else:
            number_of_instances = number_of_parties

        for idx in range(len(regions)):
            number_of_instances_to_deploy = self.check_running_instances(regions[idx], machine_type)

            if idx < number_duplicated_servers:
                number_of_instances_to_deploy = (number_of_instances - number_of_instances_to_deploy) + 1
            else:
                number_of_instances_to_deploy = number_of_instances - number_of_instances_to_deploy

            if number_of_instances_to_deploy > 0:

                # create availability set, vnet and subnet
                av_set_id = self.create_availability_set(regions[idx], protocol_name)
                self.create_vnet(regions[idx], protocol_name)
                self.create_subnet(protocol_name)
                nsg = self.network_client.network_security_groups.get(self.resource_group, 'MatrixNSG').id

                for idx2 in range(number_of_instances_to_deploy):

                    self.create_public_ip_address(regions[idx], '%s_%d' % (protocol_name, idx2))
                    nic = self.create_nic(regions[idx], protocol_name, '%s_%d_IP' % (protocol_name, idx2))

                    vm_params = {
                        'location': regions[idx],
                        'hardware_profile': {
                                'vm_size': machine_type
                            },
                        'storage_profile': {
                                'image_reference': {
                                        'id': '/subscriptions/e500fb85-1759-463b-b828-0d4e0b38a305/resourceGroups/'
                                              'MatrixRG/providers/Microsoft.Compute/images/libscapiImageEastUS'
                                    }
                            },
                        'network_profile': {
                                'network_interfaces': [{
                                    'id': nic.id
                                }]
                            },
                        'availability_set': {
                                'id': av_set_id
                            },
                        'network_security_group': {
                            'id': nsg
                        },
                        'osProfile': {
                            'adminUsername': 'ubuntu',
                            'computerName': '%s%d' % (protocol_name, idx2),
                            'linux_configuration': {
                                'disable_password_authentication': True,
                                'ssh': {
                                    'public_keys': [{
                                        'path': '/home/ubuntu/.ssh/authorized_keys',
                                        'key_data': key_data
                                    }]
                                }
                            }
                        }
                    }
                    vm = self.compute_client.virtual_machines.create_or_update('MatrixRG', '%s%d'
                                                                               % (protocol_name, idx2), vm_params)
        # wait for the machine will be online
        time.sleep(300)
        self.get_network_details()

    def get_network_details(self, port_number=8000, file_name='parties.conf', new_format=False):
        """
        Creates network topology file for the parties that participates in the protocol
        :param port_number:
        :param file_name:
        :param new_format:
        :return:
        """
        protocol_name = self.protocol_config['protocol']
        regions = self.protocol_config['CloudProviders']['azure']['regions']
        number_of_parties = self.protocol_config['CloudProviders']['azure']['numOfParties']
        for idx in range(len(regions)):
            for idx2 in range(number_of_parties):
                # save the public ip
                self.public_ips.append(self.network_client.public_ip_addresses.get(self.resource_group,
                                                                                   '%s_%d_IP'
                                                                                   % (protocol_name, idx2)).ip_address)
                nic = self.network_client.network_interfaces.get(self.resource_group, '%s_%d_Nic'
                                                                 % (protocol_name, idx2))
                self.private_ips.append(nic.ip_configurations[0].private_ip_address)

        if len(regions) > 1:
            shuffle(self.public_ips)
            self.create_parties_file(self.public_ips, port_number, file_name, new_format, len(regions))
        elif len(self.protocol_config['CloudProviders']) > 1:
            self.create_parties_file(self.public_ips, port_number, file_name, new_format, len(regions))
        else:
            self.create_parties_file(self.private_ips, port_number, file_name, new_format, len(regions))

        # write public ips to file for fabric
        if len(self.protocol_config['CloudProviders']) > 1:
            mode = 'a+'
        else:
            mode = 'w+'
        with open('InstancesConfigurations/public_ips', mode) as public_ip_file:
            for public_idx in range(len(self.public_ips)):
                public_ip_file.write('%s\n' % self.public_ips[public_idx])

    def describe_instances(self, region_name, machines_name):
        """
        Return the machines objects according to region name and machine name
        :param region_name:
        :param machines_name:
        :return: list of machines objects
        """
        response = self.compute_client.virtual_machines.list(self.resource_group)
        machines = []
        for machine in response:
            machines.append(machine)

        return machines

    def check_running_instances(self, region, machine_type):
        protocol_name = self.protocol_config['protocol']
        ready_instances = 0
        response = self.describe_instances(region, protocol_name)

        for machine in response:
            if protocol_name in machine.name and machine.hardware_profile.vm_size == machine_type:
                status = self.compute_client.virtual_machines.get(self.resource_group, machine.name, 'instanceview')
                state = status.instance_view.statuses[1].display_status
                if state == 'VM running':
                    ready_instances += 1
        return ready_instances

    def start_instances(self):
        protocol_name = self.protocol_config['protocol']
        response = self.describe_instances('eastus', protocol_name)
        for machine in response:
            m = self.compute_client.virtual_machines.start(self.resource_group, machine.name)

    def stop_instances(self):
        protocol_name = self.protocol_config['protocol']
        response = self.describe_instances('eastus', protocol_name)
        for machine in response:
            m = self.compute_client.virtual_machines.deallocate(self.resource_group, machine.name)

    def terminate_instances(self):
        protocol_name = self.protocol_config['protocol']
        response = self.describe_instances('eastus', protocol_name)

        for idx in range(len(response)):
            disk_name = response[idx].storage_profile.os_disk.name

            delete_vm = self.compute_client.virtual_machines.delete(self.resource_group, response[idx].name)
            delete_vm.wait()

            # delete disk
            self.compute_client.disks.delete(self.resource_group, disk_name)

            # delete nic
            nic = self.network_client.network_interfaces.get(self.resource_group, '%s_%d_Nic' % (protocol_name, idx))
            self.network_client.network_interfaces.delete(self.resource_group, nic.name)

            # delete IP
            ip = self.network_client.public_ip_addresses.get(self.resource_group, '%s_%d_IP' % (protocol_name, idx))
            self.network_client.public_ip_addresses.delete(self.resource_group, ip.name)

        # delete vnet
        subnet_info = self.network_client.subnets.get(
            self.resource_group,
            '%sVNet' % protocol_name,
            '%sSubnet' % protocol_name
        )
        self.network_client.subnets.delete(self.resource_group, '%sVNet' % protocol_name, subnet_info.name)
        self.network_client.virtual_networks.delete(self.resource_group, '%sVNet' % protocol_name)

        # delete availability set
        self.compute_client.availability_sets.delete(self.resource_group, '%sAVSet' % protocol_name)

    def change_instance_types(self):
        raise NotImplementedError


# TODO: https://github.com/Azure-Samples/virtual-machines-python-manage/blob/master/example.py
