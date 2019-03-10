import os
import copy
import subprocess
import shutil
import certifi
from elasticsearch import Elasticsearch


class DeployCP:
    """
    The class represent deployment object. the class is abstract
    """
    def __init__(self, protocol_config):
        """
        :type protocol_config basestring
        :param protocol_config: the configuration of the protocol we want to deploy
        """
        self.protocol_config = protocol_config
        self.es = Elasticsearch('3.81.191.221:9200', ca_certs=certifi.where())

    def create_key_pair(self):
        """
        Creates ssh keys
        :return:
        """
        raise NotImplementedError

    def create_security_group(self):
        """
        Creates security groups
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def check_latest_price(instance_type, region):
        """
        Check what is the latest winning price for spot requests
        :type instance_type basestring
        :param instance_type: the type of the machines the protocol uses
        :type region basestring
        :param region: the regions that the instances are located
        :return: the last wining price
        """
        raise NotImplementedError

    def deploy_instances(self):
        """
        Deploy instances at the requested cloud provider (CP) as configured by self.protocol_config
        :return:
        """
        raise NotImplementedError

    def check_running_instances(self, region, machine_type):
        """
        Check how many instances are online
        :type region basestring
        :param region: the regions that the instances are located
        :type machine_type basestring
        :param machine_type: the type of the machines the protocol uses
        :return: number of online instances that associated to the protocol
        """
        raise NotImplementedError

    def describe_instances(self, region_name, machines_name):
        """
        Retrieve all the machines associated to the protocol
        :type region_name basestring
        :param region_name: the regions that the instances are located
        :type machines_name basestring
        :param machines_name: the protocol name
        :return list of instances
        """
        raise NotImplementedError

    def start_instances(self):
        """
        Turn on the instances
        """
        raise NotImplementedError

    def stop_instances(self):
        """
        Turn off the instances
        """
        raise NotImplementedError

    def terminate_instances(self):
        """
        delete the instances
        """
        raise NotImplementedError

    def change_instance_types(self):
        """
        Change the type of the instance the protocol uses.
        The new type should be specified at the protocol configuration file.
        """
        raise NotImplementedError

    @staticmethod
    def create_parties_files_multi_regions(file_name):
        """
        Creates network topology file for each party
        :type file_name basestring
        :param file_name: the name of the file
        """
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
        """
        Creates party file for all the parties
        :type ip_addresses list
        :param ip_addresses: IP addresses of the instances
        :type port_number int
        :param port_number: base port number
        :type file_name basestring
        :param file_name: the name of the file
        :type new_format bool
        :param new_format: using the new format or not
        :type number_of_regions int
        :param number_of_regions: number of regions the protocol executed
        """
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
        """
        Creates party file for all the parties when using localhost or pre defined servers (on-premise)
        :type port_number int
        :param port_number: base port number
        :type file_name basestring
        :param file_name: the name of the file
        :type new_format bool
        :param new_format: using the new format or not
        """
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
            os.system('cp %s %s/InstancesConfigurations/public_ips' % (server_file, os.getcwd()))

            server_ips = []
            with open('%s/InstancesConfigurations/public_ips' % os.getcwd(), 'r+') as server_ips_file:
                for line in server_ips_file:
                    server_ips.append(line)
            self.create_parties_file(server_ips, port_number, file_name, False)

