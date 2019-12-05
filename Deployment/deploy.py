import os
import copy


class DeployCP:
    """
    The class represents deployment object. the class is abstract
    """
    def __init__(self, protocol_config):
        """
        :type protocol_config str
        :param protocol_config: the configuration of the protocol we want to deploy
        """
        self.protocol_config = protocol_config
        self.protocol_name = self.protocol_config['protocolName']

    def create_key_pair(self):
        """
        Creates private key file
        :return:
        """
        raise NotImplementedError

    def create_security_group(self):
        """
        Creates firewall rules
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def check_latest_price(instance_type, region):
        """
        Check what is the latest winning price for spot requests
        :type instance_type str
        :param instance_type: the type of the machines the protocol uses
        :type region str
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
        :type region str
        :param region: the regions that the instances are located
        :type machine_type str
        :param machine_type: the type of the machines the protocol uses
        :return: number of online instances that associated to the protocol
        """
        raise NotImplementedError

    def describe_instances(self, region_name, machines_name):
        """
        Retrieve all the machines associated to the protocol
        :type region_name str
        :param region_name: the regions that the instances are located
        :type machines_name str
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
        Shut down the instances
        """
        raise NotImplementedError

    def reboot_instances(self):
        """
        Reboots the instances. Use this method if you want to reboot the instances.
        It will save you money instead of stop->start
        """
        raise NotImplementedError

    def terminate_instances(self):
        """
        Deletes the instances
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
        :type file_name str
        :param file_name: the name of the file
        """
        try:
            with open(f'{os.getcwd()}/InstancesConfigurations/{file_name}', 'r') as origin_file:
                parties = origin_file.readlines()
        except EnvironmentError:
            print(f'Cannot open {file_name}')
            return

        number_of_parties = len(parties) // 2

        for idx in range(number_of_parties):
            new_parties = copy.deepcopy(parties)
            new_parties[idx] = 'party_%s_ip=0.0.0.0\n' % idx

            # write data to file
            try:
                with open('%s/InstancesConfigurations/parties%s.conf' % (os.getcwd(), idx), 'w+') as new_file:
                    new_file.writelines(new_parties)
            except EnvironmentError:
                print(f'Cannot write parties{idx}')

    def create_parties_file(self, ip_addresses, port_number, file_name, new_format=False, number_of_regions=1):
        """
        Creates party file for all the parties
        :type ip_addresses list
        :param ip_addresses: IP addresses of the instances
        :type port_number int
        :param port_number: base port number
        :type file_name str
        :param file_name: the name of the file
        :type new_format bool
        :param new_format: using the new format or not
        :type number_of_regions int
        :param number_of_regions: number of regions the protocol executed
        """
        regions = []
        if len(self.protocol_config['cloudProviders']) > 1:
            mode = 'a+'
        else:
            mode = 'w+'

        if 'AWS' in self.protocol_config['cloudProviders']:
            regions += self.protocol_config['cloudProviders']['AWS']['regions']
        elif 'Azure' in self.protocol_config['cloudProviders']:
            regions += self.protocol_config['cloudProviders']['Azure']['regions']
        else:
            print('Cloud provider did not found. Program will exit now')
            return
        try:
            with open(f'{os.getcwd()}/InstancesConfigurations/{file_name}', mode) as private_ip_file:
                # for backward compatibility
                if not new_format:
                    for party_idx, ip_addr in enumerate(ip_addresses):
                        private_ip_file.write(f'party_{party_idx}_ip={ip_addr}\n')

                    for port_idx in range(len(ip_addresses)):
                        if len(regions) == 0:
                            private_ip_file.write(f'party_{port_idx}_port={port_number + (port_idx * 20)}\n')
                        else:
                            private_ip_file.write(f'party_{port_idx}_port={port_number}\n')

                else:
                    for party_idx, ip_addr in enumerate(ip_addresses):
                        if len(regions) == 0:
                            private_ip_file.write(f'{ip_addr}:{port_number + (party_idx * 20)}\n')
                        else:
                            private_ip_file.write(f'{ip_addr}:8000\n')

        except EnvironmentError:
            print(f'Cannot write to {file_name}')

        # create party file for each instance
        if number_of_regions > 1:
            self.create_parties_files_multi_regions(file_name)

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
        cp = self.protocol_config['cloudProviders']
        if 'local' in cp:
            number_of_parties = cp['local']['numOfParties']
            public_ip_address = []
            for ip_idx in range(number_of_parties):
                public_ip_address.append('127.0.0.1')
            try:
                with open(f'{os.getcwd()}/InstancesConfigurations/public_ips', 'w+') as local_ips:
                    for line in public_ip_address:
                        local_ips.write(f'{line}\n')
            except EnvironmentError:
                print('Cannot write public IPs')
            self.create_parties_file(public_ip_address, port_number, file_name, False)

        # read servers configuration
        elif 'servers' in cp:
            server_file = input('Enter your server file configuration: ')
            os.system(f'cp {server_file} {os.getcwd()}/InstancesConfigurations/public_ips')

            server_ips = []
            try:
                with open(f'{os.getcwd()}/InstancesConfigurations/public_ips', 'r') as server_ips_file:
                    for line in server_ips_file:
                        server_ips.append(line)
            except EnvironmentError:
                print('Cannot read public IPs')
            self.create_parties_file(server_ips, port_number, file_name, False)

