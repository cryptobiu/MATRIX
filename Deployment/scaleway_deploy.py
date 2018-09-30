import os
import json
import time

from scaleway.apis import AccountAPI
from scaleway.apis import ComputeAPI

from Deployment.deploy import DeployCP


class ScalewayCP(DeployCP):
    def __init__(self, protocol_config):
        super(ScalewayCP, self).__init__(protocol_config)
        with open('%s/GlobalConfigurations/tokens.json' % os.getcwd()) as gc_file:
            data = json.load(gc_file)
            self.token = data['scalewayToken']
            self.account_id = self.get_account_data()['organizations'][0]['id']

    def get_account_data(self):
        api = AccountAPI(auth_token=self.token)
        res = api.query().organizations.get()
        return res

    def create_key_pair(self):
        print('Scaleway API does not supports create key pairs from an API.\n'
              'Please refer to Scaleway Web UI at https://cloud.scaleway.com/#/credentials')

    def create_security_group(self):
        regions = list(self.protocol_config['regions'].values())
        for idx in range(len(regions)):
            api = ComputeAPI(auth_token=self.token, region=regions[idx])
            api.query().security_groups.post({
                'organization': self.account_id,
                'name': 'MatrixSG%s' % regions[idx],
                'description': 'Default security group for MATRIX system'
            })

    @staticmethod
    def check_latest_price(instance_type, region):
        print('Scaleway does not supports spot instances')

    def deploy_instances(self):

        protocol_name = self.protocol_config['protocol']
        machine_type = self.protocol_config['aWSInstType']
        regions = list(self.protocol_config['regions'].values())
        number_of_parties = list(self.protocol_config['numOfParties'].values())
        number_duplicated_servers = 0

        if len(regions) > 1:
            number_of_instances = max(number_of_parties) // len(regions)
            if max(number_of_parties) % len(regions):
                number_duplicated_servers = max(number_of_parties) % len(regions)
        else:
            number_of_instances = max(number_of_parties)

        for idx in range(len(regions)):
            api = ComputeAPI(auth_token=self.token, region=regions[idx])
            number_of_instances_to_deploy = self.check_running_instances(regions[idx], machine_type)

            if idx < number_duplicated_servers:
                number_of_instances_to_deploy = (number_of_instances - number_of_instances_to_deploy) + 1
            else:
                number_of_instances_to_deploy = number_of_instances - number_of_instances_to_deploy

            print('Deploying instances :\nregion : %s\nnumber of instances : %s\ninstance_type : %s\n'
                  % (regions[idx], number_of_instances_to_deploy, machine_type))
            for idx2 in range(number_of_instances_to_deploy):

                res = api.query().servers.post({
                    'name': protocol_name,
                    'organization': self.account_id,
                    'image': 'a78f9025-5984-4880-b148-e63442edbc82',
                    'commercial_type': machine_type
                })
                server_id = res['server']['id']
                api.query().servers(server_id).action.post({'action': 'poweron'})

        time.sleep(240)
        self.get_network_details()

    def get_network_details(self, port_number=8000, file_name='parties.conf'):
        regions = list(self.protocol_config['regions'].values())
        public_ip_address = []
        private_ip_address = []
        protocol_name = self.protocol_config['protocol']

        for region in regions:
            instances = self.describe_instances(region, protocol_name)
            for instance in instances:
                if instance['state'] == 'running':
                    public_ip_address.append(instance['public_ip']['address'])
                    private_ip_address.append(instance['private_ip'])

        self.create_parties_file(private_ip_address, port_number, file_name, False)

        # write public ips for fabric
        with open('%s/InstancesConfigurations/public_ips' % os.getcwd(), 'w+') as ips_file:
            for ip in public_ip_address:
                ips_file.write('%s\n' % ip)

    def describe_instances(self, region_name, machines_name):
        api = ComputeAPI(region=region_name, auth_token=self.token)
        servers = api.query().servers.get()
        instances = []
        for server in servers['servers']:
            if server['hostname'] == machines_name:
                instances.append(server)
        return instances

    def check_running_instances(self, region, machine_type):
        protocol_name = self.protocol_config['protocol']
        machine_type = self.protocol_config['aWSInstType']
        number_of_instances = 0

        servers = self.describe_instances(region, protocol_name)

        for server in servers:
            if server['commercial_type'] == machine_type and server['state'] == 'running':
                number_of_instances += 1

        return number_of_instances

    def start_instances(self):
        protocol_name = self.protocol_config['protocol']
        regions = list(self.protocol_config['regions'].values())

        for region in regions:
            api = ComputeAPI(region=region, auth_token=self.token)
            servers = self.describe_instances(region, protocol_name)
            for server in servers:
                if not server['state'] == 'running':
                    server_id = server['id']
                    api.query().servers(server_id).action.post({'action': 'poweron'})

    def stop_instances(self):
        protocol_name = self.protocol_config['protocol']
        regions = list(self.protocol_config['regions'].values())

        for region in regions:
            api = ComputeAPI(region=region, auth_token=self.token)
            servers = self.describe_instances(region, protocol_name)
            for server in servers:
                if server['state'] == 'running':
                    server_id = server['id']
                    api.query().servers(server_id).action.post({'action': 'poweroff'})

    def terminate(self):
        protocol_name = self.protocol_config['protocol']
        regions = list(self.protocol_config['regions'].values())

        for region in regions:
            api = ComputeAPI(region=region, auth_token=self.token)
            servers = self.describe_instances(region, protocol_name)
            for server in servers:
                if server['state'] == 'stopped' or server['state'] == 'stopped in place':
                    server_id = server['id']
                    volume_id = server['volumes']['0']['id']
                    ip_id = server['public_ip']['id']

                    # delete volume
                    api.query().volumes(volume_id).delete()

                    # delete ip
                    api.query().ips(ip_id).delete()

                    # delete server
                    api.query().servers(server_id).delete()

    def change_instance_types(self):
        print('Scaleway does not support changing instance types')