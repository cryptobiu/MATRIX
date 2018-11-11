import os
import json
import copy
import subprocess
import shutil
from collections import OrderedDict


class DeployCP:
    def __init__(self, protocol_config):
        self.protocol_config = protocol_config

    @staticmethod
    def generate_circuits():
        # Synthetic circuits generation
        parties = [2, 3, 4, 8, 16, 32, 64, 128]
        depth = [10, 100, 1000, 10000, 100000, 1000000]
        mult_gates = [10000, 100000, 1000000, 10000000, 100000000, 1000000000]
        gates = [g * 4 for g in mult_gates]
        inputs = [[int(i * 0.01) for i in mult_gates], [int(i * 0.05) for i in mult_gates],
                  [int(i * 0.1) for i in mult_gates], [int(i * 0.5) for i in mult_gates]]

        for idx in range(len(parties)):
            for idx2 in range(len(inputs)):
                for idx3 in range(len(inputs[idx2])):
                    subprocess.call(['java', '-jar', 'Circuits/GenerateArythmeticCircuitForDepthAndGates.jar',
                                     str(gates[idx3]), str(mult_gates[idx3]), str(depth[idx3]),
                                     str(parties[idx]), str(inputs[idx2][idx3]), '50', 'true'], shell=False,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        shutil.move('*.txt', 'Circuits')

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

    def terminate_instances(self):
        raise NotImplementedError

    def change_instance_types(self):
        raise NotImplementedError

    @staticmethod
    def create_parties_files_multi_regions(file_name):
        with open('%s/InstancesConfigurations/%s' % (os.getcwd(), file_name), 'r') as origin_file:
            parties = origin_file.readlines()

        number_of_parties = len(parties) // 2

        for idx in range(number_of_parties):
            new_parties = copy.deepcopy(parties)
            new_parties[idx] = 'party_%s_ip=0.0.0.0\n' % idx

            # write data to file
            with open('%s/InstancesConfigurations/parties%s.conf' % (os.getcwd(), idx), 'w+') as new_file:
                new_file.writelines(new_parties)

    def create_parties_file(self, ip_addresses, port_number, file_name, new_format=True, number_of_regions=1):
        regions = []
        if len(self.protocol_config['CloudProviders']) > 1:
            mode = 'a+'
        else:
            mode = 'w+'

        if 'aws' in self.protocol_config['CloudProviders'] and 'scaleway' in self.protocol_config['CloudProviders']:
            regions = self.protocol_config['CloudProviders']['aws']['regions'] + \
                      self.protocol_config['CloudProviders']['scaleway']['regions']
        elif 'aws' in self.protocol_config['CloudProviders']:
            regions = self.protocol_config['CloudProviders']['aws']['regions']
        elif 'scaleway' in self.protocol_config['CloudProviders']:
            regions = self.protocol_config['CloudProviders']['scaleway']['regions']

        with open('%s/InstancesConfigurations/%s' % (os.getcwd(), file_name), mode) as private_ip_file:
            if not new_format:
                for party_idx in range(len(ip_addresses)):
                    private_ip_file.write('party_%s_ip=%s\n' % (party_idx, ip_addresses[party_idx]))

                for port_idx in range(len(ip_addresses)):
                    if len(regions) == 0:
                        private_ip_file.write('party_%s_port=%s\n' % (port_idx, port_number + (port_idx * 20)))
                    else:
                        private_ip_file.write('party_%s_port=%s\n' % (port_idx, port_number))

            else:
                for party_idx in range(len(ip_addresses)):
                    if len(regions) == 0:
                        private_ip_file.write('%s:%s\n' % (ip_addresses[party_idx], port_number + (party_idx * 20)))
                    else:
                        private_ip_file.write('%s:8000\n' % ip_addresses[party_idx])

        # create party file for each instance
        if number_of_regions > 1:
            self.create_parties_files_multi_regions(file_name)

    def get_network_details(self, port_number=8000, file_name='parties.conf', new_format=False):
        cp = self.protocol_config['CloudProviders']
        if 'local' in cp:
            number_of_parties = cp['local']['numOfParties']
            public_ip_address = []
            for ip_idx in range(number_of_parties):
                public_ip_address.append('127.0.0.1')
            with open('%s/InstancesConfigurations/public_ips' % os.getcwd(), 'w+') as local_ips:
                for line in public_ip_address:
                    local_ips.write('%s\n' % line)
            self.create_parties_file(public_ip_address, port_number, file_name, False)

            # read servers configuration
        elif 'servers' in cp:
            server_file = input('Enter your server file configuration: ')
            os.system('mv %s %s/InstancesConfigurations/public_ips' % (os.getcwd(), server_file))

            server_ips = []
            with open('%s/InstancesConfigurations/public_ips' % os.getcwd(), 'r+') as server_ips_file:
                for line in server_ips_file:
                    server_ips.append(line)
            self.create_parties_file(server_ips, port_number, file_name, False)

