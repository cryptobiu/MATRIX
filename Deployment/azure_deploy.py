import json

from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.servicemanagement import ServiceManagementService

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

    def create_key_pair(self):
        raise NotImplementedError

    def create_security_group(self):
        raise NotImplementedError

    @staticmethod
    def check_latest_price(instance_type, region):
        raise NotImplementedError

    def deploy_instances(self):
        resource_client = ResourceManagementClient(self.credentials, self.subscription_id)
        compute_client = ComputeManagementClient(self.credentials, self.subscription_id)
        network_client = NetworkManagementClient(self.credentials, self.subscription_id)
        resource_client.providers.register('Microsoft.Compute')
        resource_client.providers.register('Microsoft.Network')

        with open('GlobalConfigurations/azureRegions.json', 'r') as gc:
            data = json.load(gc)
            key_data = data['eastus']['keyData']

        region_name = 'eastus'
        ###########
        # create nic
        # create vnet
        async_vnet_creation = network_client.virtual_networks.create_or_update(
            'MatrixRG',
            'MatrixVNet',
            {
                'location': region_name,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            }
        )
        async_vnet_creation.wait()

        # create subnet
        async_subnet_creation = network_client.subnets.create_or_update('MatrixRG', 'MatrixVNet',
                                                                        'MatrixSubNet',
                                                                        {'address_prefix': '10.0.0.0/24'})
        subnet_info = async_subnet_creation.result()
        async_nic_creation = network_client.network_interfaces.create_or_update('MatrixRG', 'MatrixNic',
                                                                                {
                                                                                    'location': region_name,
                                                                                    'ip_configurations': [{
                                                                                        'name': 'sample-ip',
                                                                                        'subnet': {
                                                                                            'id': subnet_info.id
                                                                                        }
                                                                                    }]
                                                                                })
        nic = async_nic_creation.result().id
        vm_params = {
            'location': region_name,
            'hardware_profile':
                {
                    'vm_size': 'Standard_DS1_v2'
                },
            'storage_profile':
                {
                    'image_reference':
                        {
                            'id': '/subscriptions/e500fb85-1759-463b-b828-0d4e0b38a305/resourceGroups/MatrixRG/'
                                  'providers/Microsoft.Compute/images/libscapiImageEastUS'
                        }
                },
            'network_profile':
                {
                    'network_interfaces': [{
                        'id': nic
                    }]
                },
            'osProfile': {
                'adminUsername': 'ubuntu',
                'computerName': 'myVM',
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
        vm = compute_client.virtual_machines.create_or_update('MatrixRG', 'Test', vm_params)

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
            if machine.name == protocol_name and machine.hardware_profile.vm_size == machine_type:
                status = self.compute_client.virtual_machines.get(self.resource_group, machine.name, 'instanceview')
                state = status.instance_view.statuses[1].display_status
                if status == 'Running':
                    ready_instances += 1

    def start_instances(self):
        # self.check_running_instances('eastus', 'Standard_D2s_v3')
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
        for machine in response:
            m = self.compute_client.virtual_machines.delete(self.resource_group, machine.name)

    def change_instance_types(self):
        raise NotImplementedError


# TODO: https://github.com/Azure-Samples/virtual-machines-python-manage/blob/master/example.py
