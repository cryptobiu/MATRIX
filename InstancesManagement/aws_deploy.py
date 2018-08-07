import os
import json
import time
import boto3
import botocore

from random import shuffle
from datetime import datetime
from os.path import expanduser
from botocore import exceptions
from collections import OrderedDict

from InstancesManagement.deploy import DeployCP


class AmazonCP(DeployCP):
    def __init__(self, conf_file):
        super(AmazonCP, self).__init__(conf_file)

    def create_key_pair(self):
        regions = list(self.conf['regions.json'].values())

        for regions_idx in range(len(regions)):
            client = boto3.client('ec2', region_name=regions[regions_idx][:-1])
            keys = client.describe_key_pairs()
            number_of_current_keys = len(keys['KeyPairs'])
            try:
                key_idx = number_of_current_keys + 1
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
        regions = list(self.conf['regions.json'].values())

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
        machine_type = self.conf['aWSInstType']
        price_bids = self.conf['aWWSBidPrice']
        number_of_parties = list(self.conf['numOfParties'].values())
        regions = list(self.conf['regions'].values())
        number_duplicated_servers = 0
        spot_request = self.conf['isSpotRequest']
        protocol_name = self.conf['protocol']

        with open('%s/GlobalConfigurations/regions.json' % os.getcwd()) as gc_file:
            global_config = json.load(gc_file, object_pairs_hook=OrderedDict)

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

            number_of_instances_to_deploy = self.check_running_instances(regions[idx][:-1], machine_type)
            if idx < number_duplicated_servers:
                number_of_instances_to_deploy = (number_of_instances - number_of_instances_to_deploy) + 1
            else:
                number_of_instances_to_deploy = number_of_instances - number_of_instances_to_deploy

            print('Deploying instances :\nregion : %s\nnumber of instances : %s\nami_id : %s\ninstance_type : %s\n'
                  'valid until : %s' % (regions[idx], number_of_instances_to_deploy,
                                        global_config[regions[idx][:-1]]["ami"], machine_type, str(new_date)))

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
                                    'ImageId': global_config[regions[idx][:-1]]["ami"],
                                    'KeyName': global_config[regions[idx][:-1]]["key"],
                                    'SecurityGroups': [global_config[regions[idx][:-1]]["securityGroup"]],
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
                        BlockDeviceMappings=
                        [
                            {
                                'DeviceName': '/dev/sda1',
                                'Ebs':
                                {
                                    'DeleteOnTermination': True,
                                    'VolumeSize': 80
                                }
                            },
                            {
                                'DeviceName': '/dev/sdf',
                                'NoDevice': ''
                            }
                        ],
                        ImageId=global_config[regions[idx][:-1]]["ami"],
                        KeyName=global_config[regions[idx][:-1]]["key"],
                        MinCount=int(number_of_instances_to_deploy),
                        MaxCount=int(number_of_instances_to_deploy),
                        SecurityGroups=[global_config[regions[idx][:-1]]["securityGroup"]],
                        InstanceType=machine_type,
                        Placement=
                        {
                            'AvailabilityZone': regions[idx],
                        },
                        TagSpecifications=[{
                                            'ResourceType': 'instance',
                                            'Tags':
                                            [{
                                                    'Key': 'Name',
                                                    'Value': protocol_name
                                            }]
                                        }]
                    )

        print('Waiting for the images to be deployed..')
        time.sleep(240)
        self.get_network_details()

        print('Finished to deploy machines')

    def get_aws_network_details(self, port_counter, file_name, new_format=False):
        regions = list(self.conf['regions'].values())
        is_spot_request = self.conf['isSpotRequest']
        coordinator_exists = 'coordinatorConfig' in self.conf
        instance_type = self.conf['aWSInstType']
        protocol_name = self.conf['protocol']

        instances_ids = []
        public_ip_address = []
        private_ip_address = []

        # get the spot instances ids
        for idx in range(len(regions)):
            client = boto3.client('ec2', region_name=regions[idx][:-1])
            if is_spot_request == 'True':
                response = client.describe_instances(Filters=[{'Name': 'instance-lifecycle', 'Values': ['spot']},
                                                              {'Name': 'instance-type', 'Values': [instance_type]},
                                                              {'Name': 'tag:Name', 'Values': protocol_name}])

            else:
                response = client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [protocol_name]}])

            # Extract instances ids
            for res_idx in range(len(response['Reservations'])):
                reservations_len = len(response['Reservations'][res_idx]['Instances'])
                for reserve_idx in range(reservations_len):
                    if response['Reservations'][res_idx]['Instances'][reserve_idx]['State']['Name'] == 'running':
                        if len(regions) == 1:
                            private_ip_address.append(response['Reservations'][res_idx]['Instances'][reserve_idx]
                                                      ['NetworkInterfaces'][0]['PrivateIpAddress'])
                        instances_ids.append(response['Reservations'][res_idx]['Instances'][reserve_idx]['InstanceId'])
                        public_ip_address.append(response['Reservations'][res_idx]
                                                 ['Instances'][reserve_idx]['PublicIpAddress'])

            # check if InstancesConfigurations dir exists
            if not os.path.isdir('%s/InstancesConfigurations' % os.getcwd()):
                os.makedirs('%s/InstancesConfigurations' % os.getcwd())

        if coordinator_exists == 'True':
            del private_ip_address[0]

        # rearrange the list that the ips from the same regions.json will not be followed
        if len(regions) > 1:
            shuffle(public_ip_address)
            self.create_parties_file(public_ip_address, port_counter, file_name, new_format, len(regions))
        else:
            self.create_parties_file(private_ip_address, port_counter, file_name,  new_format, len(regions))

        # write public ips to file for fabric
        if 'local' in regions or 'server' not in regions:
            with open('InstancesConfigurations/public_ips', 'w+') as public_ip_file:
                for public_idx in range(len(public_ip_address)):
                    public_ip_file.write('%s\n' % public_ip_address[public_idx])

    def get_network_details(self, port_counter=8000, file_name='parties.conf'):
        regions = list(self.conf['regions'].values())

        number_of_parties = max(list(self.conf['numOfParties'].values()))
        if 'local' in regions:
            public_ip_address = []
            for ip_idx in range(len(number_of_parties)):
                public_ip_address.append('127.0.0.1')
            self.create_parties_file(public_ip_address, False)

        # read servers configuration
        elif 'servers' in regions:
            server_file = input('Enter your server file configuration: ')
            os.system('mv %s %s/InstancesConfigurations/public_ips' % (os.getcwd(), server_file))

            server_ips = []
            with open('%s/InstancesConfigurations/public_ips' % os.getcwd(), 'r+') as server_ips_file:
                for line in server_ips_file:
                    server_ips.append(line)
            self.create_parties_file(server_ips, False)

        else:
            self.get_aws_network_details(port_counter, file_name, False)

    def describe_instances(self, region_name, machines_name):
        client = boto3.client('ec2', region_name=region_name)
        is_spot_request = self.conf['isSpotRequest']
        if is_spot_request == 'True':
            response = client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [machines_name]},
                                                          {'Name': 'instance-lifecycle', 'Values': ['spot']}])
        else:
            response = client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [machines_name]}])
        instances = []

        for res_idx in range(len(response['Reservations'])):
            reservations_len = len(response['Reservations'][res_idx]['Instances'])
            for reserve_idx in range(reservations_len):
                instances.append(response['Reservations'][res_idx]['Instances'][reserve_idx]['InstanceId'])

        return instances

    def check_running_instances(self, region, machine_type):
        protocol_name = self.conf['protocol']
        ready_instances = 0

        client = boto3.client('ec2', region_name=region)
        response = client.describe_instances()

        for res_idx in range(len(response['Reservations'])):
            reservations_len = len(response['Reservations'][res_idx]['Instances'])
            for reserve_idx in range(reservations_len):
                if response['Reservations'][res_idx]['Instances'][reserve_idx]['State']['Name'] == 'running' and \
                        response['Reservations'][res_idx]['Instances'][reserve_idx]['Tags'][0]['Value'] == \
                        protocol_name:
                    ready_instances += 1

        return ready_instances

    def start_instances(self):
        regions = list(self.conf['regions'].values())
        machines_name = self.conf['protocol']

        for idx in range(len(regions)):
            region_name = regions[idx][:-1]
            instances = self.describe_instances(region_name, machines_name)

            client = boto3.client('ec2', region_name=region_name)
            client.start_instances(InstanceIds=instances)

    def stop_instances(self):
        regions = list(self.conf['regions'].values())
        machines_name = self.conf['protocol']

        for idx in range(len(regions)):
            region_name = regions[idx][:-1]
            instances = self.describe_instances(region_name, machines_name)

            client = boto3.client('ec2', region_name=region_name)
            client.stop_instances(InstanceIds=instances)

    def change_instance_types(self):
        regions = list(self.conf['regions'].values())
        protocol_name = self.conf['protocol']

        for idx in range(len(regions)):
            region_name = regions[idx][:-1]
            instances = self.describe_instances(region_name, protocol_name)

            client = boto3.client('ec2', region_name=region_name)
            client.stop_instances(InstanceIds=instances)
            waiter = client.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=instances)

            for instance_idx in range(len(instances)):
                # Change the instance type
                client.modify_instance_attribute(InstanceId=instances[instance_idx],
                                                 Attribute='instanceType', Value='c4.large')

            # Start the instance
            client.start_instances(InstanceIds=instances)

    def terminate(self):
        regions = list(self.conf['regions'].values())
        machines_name = self.conf['protocol']

        for idx in range(len(regions)):
            region_name = regions[idx][:-1]

            instances = self.describe_instances(region_name, machines_name)

            client = boto3.client('ec2', region_name=region_name)
            client.terminate_instances(InstanceIds=instances)
