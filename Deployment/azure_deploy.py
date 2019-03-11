import json
import time
from random import shuffle
from datetime import datetime

from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.network.models import NetworkSecurityGroup, SecurityRule
from msrestazure.azure_exceptions import CloudError

from Deployment.deploy import DeployCP


class AzureCP(DeployCP):
    """
    The class enables deployment to Azure. All the methods are valid only to Azure
    Sub class of Deployment.DeployCP
    """
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
        """
        Creates private key file. Azure does not support it.
        :return:
        """
        raise NotImplementedError

    def create_security_group(self):
        """
        Creates firewall rules
        :return:
        """
        parameters = NetworkSecurityGroup()
        parameters.location = 'useast1'

        parameters.security_rules = [SecurityRule(description='AllIn', protocol='Tcp',
                                                  source_port_range='*', destination_port_range='*', access='Allow',
                                                  direction='Inbound',  priority=100, name='AllIn'),
                                     SecurityRule(description='AllIn', protocol='Tcp',
                                                  source_port_range='*', destination_port_range='*', access='Allow',
                                                  direction='Outbound',  priority=100, name='AllIn')]
        self.network_client.network_security_groups.create_or_update(self.resource_group, "test-nsg", parameters)

    @staticmethod
    def check_latest_price(instance_type, region):
        """
        NOT supported on Azure
        Check what is the latest winning price for spot requests.
        :type instance_type str
        :param instance_type: the type of the machines the protocol uses
        :type region str
        :param region: the regions that the instances are located
        :return: the last wining price
        """
        raise NotImplementedError

    def create_availability_set(self, location, protocol_name):
        """
        Creates availability set for the instances. availability set creates instances close to each other
        :type location str
        :param location: the region that the instances are located
        :type protocol_name str
        :param protocol_name: the machines names
        :return: availability set instance
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
        :type location str
        :param location: the region that the instances are located
        :type protocol_name str
        :param protocol_name: the machines names
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
        """
        Creates virtual network at te requested location. The Virtual network will host a subnet
        :type location str
        :param location: the region that the instances are located
        :type protocol_name str
        :param protocol_name: the machines names
        :return:
        """
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
        """
        Creates subnet for the instances.
        :type protocol_name str
        :param protocol_name: the machines names
        :return:
        """
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
        """
        Creates NIC for each instance
        :type location str
        :param location: the region that the instances are located
        :type protocol_name str
        :param protocol_name: the machines names
        :type ip_name str
        :param ip_name: the public IP address name
        :return:
        """
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
        """
        Deploy instances at the requested cloud provider (CP) as configured by self.protocol_config
        :return:
        """
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
                doc = {}
                doc['protocolName'] = protocol_name
                doc['message'] = 'Deploying availability set, virtual network and subnet'
                doc['timestamp'] = datetime.utcnow()
                self.es.index(index='deployment_matrix_ui', doc_type='deployment_matrix_ui', body=doc)

                av_set_id = self.create_availability_set(regions[idx], protocol_name)
                self.create_vnet(regions[idx], protocol_name)
                self.create_subnet(protocol_name)
                nsg = self.network_client.network_security_groups.get(self.resource_group, 'MatrixNSG').id
                with open('GlobalConfigurations/azureTokens.json', 'r') as tokens:
                    data = json.load(tokens)
                    key_data = data[regions[idx]]['keyData']
                with open('GlobalConfigurations/azureRegions.json', 'r') as regions_file:
                    images = json.load(regions_file)
                    image_name = images[regions[idx]]['imageName']

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
                                              'MatrixRG/providers/Microsoft.Compute/images/%s' % image_name
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
                    doc = {}
                    doc['protocolName'] = protocol_name
                    doc['message'] = 'Deploy machine %s%d' % (protocol_name, idx2)
                    doc['timestamp'] = datetime.utcnow()
                    self.es.index(index='deployment_matrix_ui', doc_type='deployment_matrix_ui', body=doc)
                    vm = self.compute_client.virtual_machines.create_or_update('MatrixRG', '%s%d'
                                                                               % (protocol_name, idx2), vm_params)
        # wait for the machine will be online
        time.sleep(300)
        self.get_network_details()

    def get_network_details(self, port_number=8000, file_name='parties.conf', new_format=False):
        """
        Creates party file for all the parties when using localhost or pre defined servers (on-premise)
        :type port_number int
        :param port_number: base port number
        :type file_name str
        :param file_name: the name of the file
        :type new_format bool
        :param new_format: using the new format or not
        """
        protocol_name = self.protocol_config['protocol']
        regions = self.protocol_config['CloudProviders']['azure']['regions']
        number_of_parties = self.protocol_config['CloudProviders']['azure']['numOfParties']

        doc = {}
        doc['protocolName'] = protocol_name
        doc['message'] = 'Fetching network topology for protocol: %s' % protocol_name
        doc['timestamp'] = datetime.utcnow()
        self.es.index(index='deployment_matrix_ui', doc_type='deployment_matrix_ui', body=doc)

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
        Retrieve all the machines associated to the protocol
        :type region_name str
        :param region_name: the regions that the instances are located
        :type machines_name str
        :param machines_name: the protocol name
        :return list of instances
        """
        response = self.compute_client.virtual_machines.list(self.resource_group)
        machines = []
        for machine in response:
            machines.append(machine)

        return machines

    def check_running_instances(self, region, machine_type):
        """
        Check how many instances are online
        :type region str
        :param region: the regions that the instances are located
        :type machine_type str
        :param machine_type: the type of the machines the protocol uses
        :return: number of online instances that associated to the protocol
        """
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
        """
        Turn on the instances
        """
        protocol_name = self.protocol_config['protocol']
        regions = self.protocol_config['CloudProviders']['aws']['regions']
        for region in regions:
            response = self.describe_instances(region, protocol_name)

            doc = {}
            doc['protocolName'] = protocol_name
            doc['message'] = 'starting protocol: %s vms ' % protocol_name
            doc['timestamp'] = datetime.utcnow()
            self.es.index(index='deployment_matrix_ui', doc_type='deployment_matrix_ui', body=doc)

            for machine in response:
                self.compute_client.virtual_machines.start(self.resource_group, machine.name)

    def stop_instances(self):
        """
        Shut down the instances
        """
        protocol_name = self.protocol_config['protocol']
        regions = self.protocol_config['CloudProviders']['aws']['regions']
        for region in regions:
            response = self.describe_instances(region, protocol_name)

            doc = {}
            doc['protocolName'] = protocol_name
            doc['message'] = 'stopping protocol: %s vms ' % protocol_name
            doc['timestamp'] = datetime.utcnow()
            self.es.index(index='deployment_matrix_ui', doc_type='deployment_matrix_ui', body=doc)

            for machine in response:
                self.compute_client.virtual_machines.deallocate(self.resource_group, machine.name)

    def terminate_instances(self):
        """
        Reboots the instances. Use this method if you want to reboot the instances.
        It will save you money instead of stop->start
        """
        protocol_name = self.protocol_config['protocol']
        regions = self.protocol_config['CloudProviders']['aws']['regions']
        for region in regions:
            response = self.describe_instances(region, protocol_name)

            for idx in range(len(response)):

                doc = {}
                doc['protocolName'] = protocol_name
                doc['message'] = 'terminate machine: %s%d' % (protocol_name, idx)
                doc['timestamp'] = datetime.utcnow()
                self.es.index(index='deployment_matrix_ui', doc_type='deployment_matrix_ui', body=doc)

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
        """
        NOT supported on Azure
        Change the type of the instance the protocol uses.
        The new type should be specified at the protocol configuration file.
        """
        raise NotImplementedError
