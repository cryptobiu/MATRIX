import json

from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.compute.v2017_03_30.models import Sku, \
    VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings, VirtualMachineScaleSetIPConfiguration, \
    VirtualMachineScaleSetNetworkProfile
from azure.mgmt.compute.v2018_10_01.models import VirtualMachineScaleSetPublicIPAddressConfiguration
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.servicefabric.models import UpgradeMode
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
        sku = Sku(name='Standard_DS1_v2', capacity=5)
        protocol_name = self.protocol_config['protocol']

        ###########
        # create nic
        # create vnet

        # create DNS
        vmss_dns = VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings('%s_dns' % protocol_name)

        vmss_ips = VirtualMachineScaleSetPublicIPAddressConfiguration('%s_ips' % protocol_name, dns_settings=vmss_dns)

        # create public ip
        # vmss_network_config = VirtualMachineScaleSetNetworkConfiguration(
        #     protocol_name
        # )
        vmss_network_profile = VirtualMachineScaleSetNetworkProfile()

        # vmss_profile = VirtualMachineScaleSetVMProfile(storage_profile={
        #             'image_reference':
        #             {
        #                 'id': '/subscriptions/e500fb85-1759-463b-b828-0d4e0b38a305/resourceGroups/MatrixRG/'
        #                       'providers/Microsoft.Compute/images/libscapiImageEastUS'
        #             }
        #         },
        #     os_profile={
        #         'adminUsername': 'ubuntu',
        #         'computerName': 'myVM',
        #         'linux_configuration': {
        #             'disable_password_authentication': True,
        #             'ssh': {
        #                 'public_keys': [{
        #                     'path': '/home/ubuntu/.ssh/authorized_keys',
        #                     'key_data': key_data
        #                 }]
        #             }
        #         }
        #     },
        #     network_profile={
        #     'network_interfaces': [{
        #         'id': nic
        #     }]
        # })
        # upgrade_policy = UpgradePolicy('Manual')
        # # upgrade_mode = UpgradeMode(value=)
        # vmss = VirtualMachineScaleSet(region_name, sku=sku, virtual_machine_profile=vmss_profile,
        #                               upgrade_policy=upgrade_policy, single_placement_group=True)
        # response = self.compute_client.virtual_machine_scale_sets.create_or_update(self.resource_group, 'HyperMPC',
        #                                                                            vmss)

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


# TODO: https://docs.microsoft.com/en-us/python/api/azure-mgmt-compute/azure.mgmt.compute.computemanagementclient?view=azure-python
# TODO: https://docs.microsoft.com/en-us/python/api/azure-mgmt-compute/azure.mgmt.compute.v2018_04_01.operations.virtual_machine_scale_sets_operations.virtualmachinescalesetsoperations?view=azure-python
# TODO: https://stackoverflow.com/questions/54167679/azure-python-vm-scale-set-network-profile-has-no-network-interface-configuration
