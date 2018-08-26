import os
import json
import copy
from collections import OrderedDict


class DeployCP:
    def __init__(self, conf_file):
        with open(conf_file) as data_file:
            self.conf = json.load(data_file, object_pairs_hook=OrderedDict)

    def create_key_pair(self):
        raise NotImplementedError

    def create_security_group(self):
        raise NotImplementedError

    @staticmethod
    def check_latest_price(instance_type, region):
        raise NotImplementedError

    def deploy_instances(self):
        raise NotImplementedError

    def check_running_instances(self, region, machine_type):
        raise NotImplementedError

    def describe_instances(self, region_name, machines_name):
        raise NotImplementedError

    def start_instances(self):
        raise NotImplementedError

    def stop_instances(self):
        raise NotImplementedError

    def change_instance_types(self):
        raise NotImplementedError

    @staticmethod
    def create_parties_files_multi_regions(file_name):
        with open('%s/InstancesConfigurations/%s' % (os.getcwd(), file_name), 'r') as origin_file:
            parties = origin_file.readlines()

        number_of_parties = len(parties) // 2
        print(number_of_parties)

        for idx in range(number_of_parties):
            new_parties = copy.deepcopy(parties)
            new_parties[idx] = 'party_%s_ip=0.0.0.0\n' % idx

            # write data to file
            with open('%s/InstancesConfigurations/parties%s.conf' % (os.getcwd(), idx), 'w+') as new_file:
                new_file.writelines(new_parties)

    def create_parties_file(self, ip_addresses, port_number, file_name, new_format=True, number_of_regions=1):

        print('Parties network configuration')
        regions = list(self.conf['regions'].values())

        with open('%s/InstancesConfigurations/%s' % (os.getcwd(), file_name), 'w+') as private_ip_file:
            if not new_format:
                for party_idx in range(len(ip_addresses)):
                    private_ip_file.write('party_%s_ip=%s\n' % (party_idx, ip_addresses[party_idx]))

                for port_idx in range(len(ip_addresses)):
                    if 'local' in regions:
                        private_ip_file.write('party_%s_port=%s\n' % (port_idx, port_number + (port_idx * 20)))
                    else:
                        private_ip_file.write('party_%s_port=%s\n' % (port_idx, port_number))

            else:
                for party_idx in range(len(ip_addresses)):
                    if 'local' in regions:
                        private_ip_file.write('%s:%s\n' % (ip_addresses[party_idx], port_number + (party_idx * 20)))
                    else:
                        private_ip_file.write('%s:8000\n' % ip_addresses[party_idx])

        # create party file for each instance
        if number_of_regions > 1:
            self.create_parties_files_multi_regions(file_name)

    def get_network_details(self, port_number=8000, file_name='parties.conf'):
        regions = list(self.conf['regions'].values())

        number_of_parties = max(list(self.conf['numOfParties'].values()))
        if 'local' in regions:
            public_ip_address = []
            for ip_idx in range(number_of_parties):
                public_ip_address.append('127.0.0.1')
            with open('%s/InstancesConfigurations/public_ips' % os.getcwd(), 'w+') as local_ips:
                for line in public_ip_address:
                    local_ips.write('%s\n' % line)
            self.create_parties_file(public_ip_address, port_number, file_name, False)

        # read servers configuration
        elif 'servers' in regions:
            server_file = input('Enter your server file configuration: ')
            os.system('mv %s %s/InstancesConfigurations/public_ips' % (os.getcwd(), server_file))

            server_ips = []
            with open('%s/InstancesConfigurations/public_ips' % os.getcwd(), 'r+') as server_ips_file:
                for line in server_ips_file:
                    server_ips.append(line)
            self.create_parties_file(server_ips, port_number, file_name, False)
