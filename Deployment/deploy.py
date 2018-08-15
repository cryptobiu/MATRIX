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

    def create_parties_file(self, ip_addresses, port_counter, file_name, new_format=True, number_of_regions=1):

        print('Parties network configuration')
        with open('%s/InstancesConfigurations/%s' % (os.getcwd(), file_name), 'w+') as private_ip_file:
            if not new_format:
                for party_idx in range(len(ip_addresses)):
                    private_ip_file.write('party_%s_ip=%s\n' % (party_idx, ip_addresses[party_idx]))

                for port_idx in range(len(ip_addresses)):
                    private_ip_file.write('party_%s_port=%s\n' % (port_idx, port_counter))

            else:
                for party_idx in range(len(ip_addresses)):
                    private_ip_file.write('%s:8000\n' % ip_addresses[party_idx])

        # create party file for each instance
        if number_of_regions > 1:
            self.create_parties_files_multi_regions(file_name)
