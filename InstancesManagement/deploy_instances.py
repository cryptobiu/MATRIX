import os
import json
import time
import copy
import boto3
import botocore
from random import shuffle
from datetime import datetime
from os.path import expanduser
from botocore import exceptions
from collections import OrderedDict


class Deploy:
    def __init__(self, conf_file):
        self.config_file_path = conf_file

    def create_key_pair(self, number_of_parties):
        with open(self.config_file_path) as regions_file:
            data = json.load(regions_file, object_pairs_hook=OrderedDict)
            regions = list(data['regions'].values())

        for regions_idx in range(len(regions)):
            client = boto3.client('ec2', region_name=regions[regions_idx][:-1])
            keys = client.describe_key_pairs()
            number_of_current_keys = len(keys['KeyPairs'])
            for idx in range(number_of_parties):
                try:
                    key_idx = idx + number_of_current_keys + 1
                    key_pair = client.create_key_pair(KeyName='Matrix%s-%s'
                                                              % (regions[regions_idx].replace('-', '')[:-1], key_idx))
                    key_name = key_pair['KeyName']
                    with open(expanduser('~/Keys/%s' % key_name), 'w+') as key_file:
                        key_file.write(key_pair['KeyMaterial'])
                except botocore.exceptions.EndpointConnectionError as e:
                    print(e.response['Error']['Message'].upper())
                except botocore.exceptions.ClientError as e:
                    print(e.response['Error']['Message'].upper())

    def create_security_group(self):
        with open(self.config_file_path) as regions_file:
            data = json.load(regions_file, object_pairs_hook=OrderedDict)
            regions = list(data['regions'].values())

        for idx in range(len(regions)):
            client = boto3.client('ec2', region_name=regions[idx][:-1])
            # create security group
            try:
                response = client.create_security_group(
                    Description='Matrix system security group',
                    GroupName='MatrixSG%s' % regions[idx].replace('-', '')[:-1],
                    DryRun=False
                )

                # Add FW rules
                sg_id = response['GroupId']
                ec2 = boto3.resource('ec2', region_name=regions[idx][:-1])
                security_group = ec2.SecurityGroup(sg_id)
                security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=0, ToPort=65535)
            except botocore.exceptions.EndpointConnectionError as e:
                print(e.response['Error']['Message'].upper())
            except botocore.exceptions.ClientError as e:
                print(e.response['Error']['Message'].upper())

    @staticmethod
    def check_latest_price(instance_type, region):
        client = boto3.client('ec2', region_name=region[:-1])
        prices = client.describe_spot_price_history(InstanceTypes=[instance_type], MaxResults=1,
                                                    ProductDescriptions=['Linux/UNIX (Amazon VPC)'],
                                                    AvailabilityZone=region)
        return prices['SpotPriceHistory'][0]['SpotPrice']

    def deploy_instances(self):
        with open(self.config_file_path) as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)
            machine_type = data['aWSInstType']
            price_bids = data['aWWSBidPrice']
            number_of_parties = list(data['numOfParties'].values())
            amis_id = list(data['amis'].values())
            regions = list(data['regions'].values())
            number_duplicated_servers = 0
            spot_request = data['isSpotRequest']

        with open('%s/GlobalConfigurations/conf.json' % os.getcwd()) as gc_file:
            global_config = json.load(gc_file, object_pairs_hook=OrderedDict)
            keys = list(global_config['keys'].values())
            security_group = list(global_config['securityGroups'].values())

        if len(regions) > 1:
            number_of_instances = max(number_of_parties) // len(regions)
            if max(number_of_parties) % len(regions):
                number_duplicated_servers = max(number_of_parties) % len(regions)
        else:
            number_of_instances = max(number_of_parties)

        date = datetime.now().replace(hour=datetime.now().hour - 3)
        print('Current date : \n%s' % str(date))
        new_date = date.replace(hour=date.hour + 6)

        for idx in range(len(regions)):
            client = boto3.client('ec2', region_name=regions[idx][:-1])

            number_of_instances_to_deploy = self.check_running_spot_instances(regions[idx][:-1], machine_type)
            if idx < number_duplicated_servers:
                number_of_instances_to_deploy = (number_of_instances - number_of_instances_to_deploy) + 1
            else:
                number_of_instances_to_deploy = number_of_instances - number_of_instances_to_deploy

            print('Deploying instances :\nregion : %s\nnumber of instances : %s\nami_id : %s\ninstance_type : %s\n'
                  'valid until : %s' % (regions[idx], number_of_instances_to_deploy,
                                        amis_id[idx], machine_type, str(new_date)))

            if number_of_instances_to_deploy > 0:
                if spot_request == 'True':
                    # check if price isn't too low
                    winning_bid_price = self.check_latest_price(machine_type, regions[idx])
                    if float(price_bids) < float(winning_bid_price):
                        price_bids = str(winning_bid_price)
                    try:
                        client.request_spot_instances(
                                DryRun=False,
                                SpotPrice=price_bids,
                                InstanceCount=number_of_instances_to_deploy,
                                ValidUntil=new_date,
                                LaunchSpecification=
                                {
                                    'ImageId': amis_id[idx],
                                    'KeyName': keys[idx],
                                    'SecurityGroups': [security_group[idx]],
                                    'InstanceType': machine_type,
                                    'Placement':
                                        {
                                            'AvailabilityZone': regions[idx],
                                        },
                                }
                        )
                    except botocore.exceptions.ClientError as e:
                        print(e.response['Error']['Message'].upper())
                else:
                    client.run_instances(
                        ImageId=amis_id[idx],
                        KeyName=keys[idx],
                        MinCount=int(number_of_instances_to_deploy),
                        MaxCount=int(number_of_instances_to_deploy),
                        SecurityGroups=[security_group[idx]],
                        InstanceType=machine_type,
                        Placement=
                        {
                            'AvailabilityZone': regions[idx],
                        }
                    )

        print('Waiting for the images to be deployed..')
        time.sleep(240)
        self.get_network_details()

        print('Finished to deploy machines')

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

    def get_aws_network_details(self, port_number=8000, file_name='parties.conf'):
        with open(self.config_file_path) as data_file:
            data = json.load(data_file)
            regions = list(data['regions'].values())
            is_spot_request = data['isSpotRequest']
            coordinator_exists = 'coordinatorConfig' in data

        instances_ids = []
        public_ip_address = []

        if len(regions) == 1:
            private_ip_address = []

        # get the spot instances ids
        for idx in range(len(regions)):
            client = boto3.client('ec2', region_name=regions[idx][:-1])
            if is_spot_request == 'True':
                response = client.describe_spot_instance_requests()
                for req_idx in range(len(response['SpotInstanceRequests'])):
                    if response['SpotInstanceRequests'][req_idx]['State'] == 'active' or \
                            response['SpotInstanceRequests'][req_idx]['State'] == 'open':
                        instances_ids.append(response['SpotInstanceRequests'][req_idx]['InstanceId'])
            else:
                response = client.describe_instances()
                for res_idx in range(len(response['Reservations'])):
                    reservations_len = len(response['Reservations'][res_idx]['Instances'])
                    for reserve_idx in range(reservations_len):
                        if response['Reservations'][res_idx]['Instances'][reserve_idx]['State']['Name'] == 'running':
                            instances_ids.append(response['Reservations']
                                                 [res_idx]['Instances'][reserve_idx]['InstanceId'])

            # delete MATRIX server from instances ids
            if 'i-06146d4b39e3c79fb' in instances_ids:
                instances_ids.remove('i-06146d4b39e3c79fb')

            # check if InstancesConfigurations dir exists
            if not os.path.isdir('%s/InstancesConfigurations' % os.getcwd()):
                os.makedirs('%s/InstancesConfigurations' % os.getcwd())

            # save instance_ids for experiment termination
            with open('%s/InstancesConfigurations/instances_ids_%s' % (os.getcwd(), regions[idx][:-1]), 'a+') \
                    as ids_file:
                for instance_idx in range(len(instances_ids)):
                    ids_file.write('%s\n' % instances_ids[instance_idx])
                ec2 = boto3.resource('ec2', region_name=regions[idx][:-1])
                instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

                for inst in instances:
                    if inst.id in instances_ids:
                        public_ip_address.append(inst.public_ip_address)
                        if len(regions) == 1:
                            private_ip_address.append(inst.private_ip_address)

        # rearrange the list that the ips from the same regions will not be followed
        if len(regions) > 1:
            shuffle(public_ip_address)

        print('Parties network configuration')
        with open('%s/InstancesConfigurations/%s' % (os.getcwd(), file_name), 'w+') as private_ip_file:
            if len(regions) > 1:
                for public_idx in range(len(public_ip_address)):
                    print('party_%s_ip=%s' % (public_idx, public_ip_address[public_idx]))
                    private_ip_file.write('party_%s_ip=%s\n' % (public_idx, public_ip_address[public_idx]))
            else:
                if coordinator_exists == 'True':
                    del private_ip_address[0]

                for private_idx in range(len(private_ip_address)):
                    print('party_%s_ip=%s' % (private_idx, private_ip_address[private_idx]))
                    private_ip_file.write('party_%s_ip=%s\n' % (private_idx, private_ip_address[private_idx]))

            for port_idx in range(len(public_ip_address)):
                print('party_%s_port=%s' % (port_idx, port_number))
                private_ip_file.write('party_%s_port=%s\n' % (port_idx, port_number))

        # write public ips to file for fabric
        if 'local' in regions or 'server' not in regions:
            with open('InstancesConfigurations/public_ips', 'w+') as public_ip_file:
                for public_idx in range(len(public_ip_address)):
                    public_ip_file.write('%s\n' % public_ip_address[public_idx])

        # create party file for each instance
        if len(regions) > 1:
            self.create_parties_files_multi_regions(file_name)

    def get_network_details(self, port_counter=8000, file_name='parties.conf'):
        with open(self.config_file_path) as data_file:
            data = json.load(data_file)
            regions = list(data['regions'].values())

        public_ip_address = []

        number_of_parties = max(list(data['numOfParties'].values()))
        if 'local' in regions:
            with open('%s/InstancesConfigurations/%s' % (os.getcwd(), file_name), 'w+') as private_ip_file:
                for ip_idx in range(len(number_of_parties)):
                    private_ip_file.write('party_%s_ip=127.0.0.1\n' % ip_idx)
                    public_ip_address.append('127.0.0.1')

                # port_counter = 8000
                for ip_idx in range(len(number_of_parties)):
                    private_ip_file.write('party_%s_port=%s\n' % (ip_idx, port_counter))
                    port_counter += 100

        elif 'servers' in regions:
            server_file = input('Enter your server file configuration: ')
            os.system('mv %s %s/InstancesConfigurations/public_ips' % (os.getcwd(), server_file))

            server_ips = []
            with open('%s/InstancesConfigurations/public_ips' % os.getcwd(), 'r+') as server_ips_file:
                for line in server_ips_file:
                    server_ips.append(line)

                with open('%s/InstancesConfigurations/%s' % (os.getcwd(),file_name), 'w+') as private_ip_file:
                    for ip_idx in range(len(server_ips)):
                        print('party_%s_ip=%s' % (ip_idx, server_ips[ip_idx]))
                        private_ip_file.write('party_%s_ip=127.0.0.1' % ip_idx)

                    # port_counter = 8000
                    for ip_idx in range(len(server_ips)):
                        private_ip_file.write('party_%s_port=%s\n' % (ip_idx, port_counter))
        else:
            self.get_aws_network_details(port_counter, file_name)

    def get_aws_network_details_from_api(self):

        self.get_aws_network_details()
        ips = input('Enter IPs addresses separated by comma:')
        ips_splitted = ips.split(',')

        with open('%s/InstancesConfigurations/parties.conf' % os.getcwd(), 'r') as origin_file:
            parties = origin_file.readlines()

        number_of_parties = len(parties) // 2
        del parties[number_of_parties:len(parties)]

        new_parties = copy.deepcopy(parties)
        for idx in range(len(ips_splitted)):
            new_parties.append('party_%s_ip=%s\n' % (str(number_of_parties + idx),
                               ips_splitted[idx]))

        # insert ports numbers after insert ips addresses in the right places

        for idx2 in range(len(new_parties)):
            new_parties.append('party_%s_port=8000\n' % idx2)

        # write data to file
        with open('%s/InstancesConfigurations/parties.conf' % os.getcwd(), 'w+') as new_file:
            new_file.writelines(new_parties)

        # copy file to assets directory
        os.rename('%s/InstancesConfigurations/parties.conf' % os.getcwd(),
                  '%s/public/assets/parties.conf' % os.getcwd())
        # create circuit according to number of parties
        number_of_gates = 1000
        number_of_mult_gates = 1000
        depth = 20
        number_of_parties = 3
        number_of_inputs = 1000 // number_of_parties
        number_of_outputs = 50
        os.system('java -jar %s/InstancesConfigurations/GenerateArythmeticCircuitForDepthAndGates.jar '
                  '%s %s %s %s %s %s true' % (os.getcwd(), number_of_gates, number_of_mult_gates, depth,
                                              number_of_parties, number_of_inputs, number_of_outputs))

        file_name = '%sG_%sMG_%sIn_%sOut_%sD_OutputOne%sP.txt' % (number_of_gates, number_of_mult_gates,
                                                                  number_of_inputs, number_of_outputs, depth,
                                                                  number_of_parties)

        os.rename('%s/%s' % (os.getcwd(), file_name), '%s/public/assets/%s' % (os.getcwd(), file_name))

    @staticmethod
    def check_running_spot_instances(region, machine_type):

        instances_ids = list()
        instances_count = 0

        client = boto3.client('ec2', region_name=region)
        response = client.describe_spot_instance_requests()

        for req_idx in range(len(response['SpotInstanceRequests'])):
            if (response['SpotInstanceRequests'][req_idx]['State'] == 'active' or
                            response['SpotInstanceRequests'][req_idx]['State'] == 'open')\
                    and response['SpotInstanceRequests'][req_idx]['LaunchSpecification']['InstanceType'] \
                    == machine_type:
                instances_ids.append(response['SpotInstanceRequests'][req_idx]['InstanceId'])

        ec2 = boto3.resource('ec2', region_name=region)
        instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

        for inst in instances:
            if inst.id in instances_ids:
                instances_count += 1

        return instances_count

    def check_running_instances(self):
        with open(self.config_file_path) as data_file:
            data = json.load(data_file)
        regions = list(data['regions'].values())
        ready_instances = 0
        for idx in range(len(regions)):
            client = boto3.client('ec2', region_name=regions[idx][:-1])
            response = client.describe_instances()
            for res_idx in range(len(response['Reservations'])):
                reservations_len = len(response['Reservations'][res_idx]['Instances'])
                for reserve_idx in range(reservations_len):
                    if response['Reservations'][res_idx]['Instances'][reserve_idx]['State']['Name'] == 'running' and \
                            not response['Reservations'][res_idx]['Instances'][reserve_idx]['InstanceId'] == \
                            'i-06146d4b39e3c79fb':
                        ready_instances += 1

        print('**Number of ready instances : %s**' % ready_instances)
        return ready_instances

    @staticmethod
    def convert_parties_file_to_rti():
        with open('InstancesConfigurations/parties.conf', 'r') as origin_file:
            origin_data = origin_file.readlines()
            origin_data = origin_data[:len(origin_data) // 2]
            ips_addresses = ''
            for item in origin_data:
                ips_addresses += '%s,' % item[item.index('=')+1:len(item)-2]
            ips_addresses = ips_addresses[:-1]

        with open('InstancesConfigurations/parties.conf', 'w+') as new_file:
            new_file.write(ips_addresses)



