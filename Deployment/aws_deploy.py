import os
import json
import time
import boto3
import botocore

from random import shuffle
from datetime import datetime, timedelta
from pathlib import Path
from botocore import exceptions
from collections import OrderedDict

from Deployment.deploy import DeployCP


class AmazonCP(DeployCP):
    def __init__(self, protocol_config):
        super(AmazonCP, self).__init__(protocol_config)

    def create_key_pair(self):
        regions = self.protocol_config['CloudProviders']['aws']['regions']

        for regions_idx in range(len(regions)):
            client = boto3.client('ec2', region_name=regions[regions_idx][:-1])
            keys = client.describe_key_pairs()
            number_of_current_keys = len(keys['KeyPairs'])
            try:
                key_idx = number_of_current_keys + 1
                key_pair = client.create_key_pair(KeyName='Matrix%s-%s'
                                                          % (regions[regions_idx].replace('-', '')[:-1], key_idx))
                key_name = key_pair['KeyName']
                with open('%s/Keys/%s' % (Path.home(), key_name), 'w+') as key_file:
                    key_file.write(key_pair['KeyMaterial'])
            except botocore.exceptions.EndpointConnectionError as e:
                print(e.response['Error']['Message'].upper())
            except botocore.exceptions.ClientError as e:
                print(e.response['Error']['Message'].upper())

    def create_security_group(self):
        regions = self.protocol_config['CloudProviders']['aws']['regions']

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
        return float(prices['SpotPriceHistory'][0]['SpotPrice'])

    @staticmethod
    def get_ami_disk_size(region_name):
        client = boto3.client('ec2', region_name)

        with open('%s/GlobalConfigurations/regions.json' % os.getcwd()) as gc_file:
            global_config = json.load(gc_file, object_pairs_hook=OrderedDict)

        ami_id = global_config[region_name]["ami"]
        response = client.describe_images(ImageIds=[ami_id])
        return response['Images'][0]['BlockDeviceMappings'][0]['Ebs']['VolumeSize']

    def deploy_instances(self):
        regions = self.protocol_config['CloudProviders']['aws']['regions']
        if 'local' in regions or 'servers' in regions:
            self.get_network_details()
        else:
            machine_type = self.protocol_config['CloudProviders']['aws']['instanceType']
            if 'spotPrice' in self.protocol_config['CloudProviders']['aws']:
                spot_request = True
                price_bids = self.protocol_config['CloudProviders']['aws']['spotPrice']
            else:
                spot_request = False
            number_of_parties = self.protocol_config['CloudProviders']['aws']['numOfParties']
            number_duplicated_servers = 0
            protocol_name = self.protocol_config['protocol']
    
            with open('%s/GlobalConfigurations/regions.json' % os.getcwd()) as gc_file:
                global_config = json.load(gc_file, object_pairs_hook=OrderedDict)
    
            if len(regions) > 1:
                number_of_instances = number_of_parties // len(regions)
                if number_of_parties % len(regions):
                    number_duplicated_servers = number_of_parties % len(regions)
            else:
                number_of_instances = number_of_parties
    
            date = datetime.now() - timedelta(hours=3)
            print('Current date : \n%s' % str(date))
            new_date = date + timedelta(hours=6)
    
            for idx in range(len(regions)):
                client = boto3.client('ec2', region_name=regions[idx][:-1])
                disk_size = self.get_ami_disk_size(regions[idx][:-1])
    
                number_of_instances_to_deploy = self.check_running_instances(regions[idx][:-1], machine_type)
                if idx < number_duplicated_servers:
                    number_of_instances_to_deploy = (number_of_instances - number_of_instances_to_deploy) + 1
                else:
                    number_of_instances_to_deploy = number_of_instances - number_of_instances_to_deploy
    
                print('Deploying instances :\nregion : %s\nnumber of instances : %s\nami_id : %s\ninstance_type : %s\n'
                      'valid until : %s' % (regions[idx], number_of_instances_to_deploy,
                                            global_config[regions[idx][:-1]]["ami"], machine_type, str(new_date)))
    
                if number_of_instances_to_deploy > 0:
                    if spot_request:
                        # check if price isn't too low
                        winning_bid_price = self.check_latest_price(machine_type, regions[idx])
                        request_bid = min(price_bids, winning_bid_price)
                        try:
                            response = client.request_spot_instances(
                                    DryRun=False,
                                    SpotPrice=str(request_bid),
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
                            time.sleep(10)
                            spot_requests_ids = []
                            for request in response['SpotInstanceRequests']:
                                spot_requests_ids.append(request['SpotInstanceRequestId'])
                            instances_response = client.describe_spot_instance_requests(
                                Filters=[{'Name': 'spot-instance-request-id', 'Values': spot_requests_ids}])
                            instances_ids = []
                            for instance_response in instances_response['SpotInstanceRequests']:
                                instances_ids.append(instance_response['InstanceId'])
                            client.create_tags(Resources=instances_ids,Tags=[{
                                'Key': 'Name',
                                'Value': protocol_name
                            }])

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
                                        'VolumeSize': disk_size
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

    def get_network_details(self, port_number=8000, file_name='parties.conf', new_format=False):
        regions = self.protocol_config['CloudProviders']['aws']['regions']
        is_spot_request = 'spotPrice' in self.protocol_config['CloudProviders']['aws']
        coordinator_exists = 'coordinatorConfig' in self.protocol_config
        instance_type = self.protocol_config['CloudProviders']['aws']['instanceType']
        protocol_name = self.protocol_config['protocol']

        instances_ids = []
        public_ip_address = []
        private_ip_address = []

        # get the spot instances ids
        for idx in range(len(regions)):
            client = boto3.client('ec2', region_name=regions[idx][:-1])
            if is_spot_request:
                response = client.describe_instances(Filters=[{'Name': 'instance-lifecycle', 'Values': ['spot']},
                                                              {'Name': 'instance-type', 'Values': [instance_type]},
                                                              {'Name': 'tag:Name', 'Values': [protocol_name]}])

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
            self.create_parties_file(public_ip_address, port_number, file_name, new_format, len(regions))
        elif len(self.protocol_config['CloudProviders']) > 1:
            self.create_parties_file(public_ip_address, port_number, file_name, new_format, len(regions))
        else:
            self.create_parties_file(private_ip_address, port_number, file_name,  new_format, len(regions))

        # write public ips to file for fabric
        if len(self.protocol_config['CloudProviders']) > 1:
            mode = 'a+'
        else:
            mode = 'w+'
        with open('InstancesConfigurations/public_ips', mode) as public_ip_file:
            for public_idx in range(len(public_ip_address)):
                public_ip_file.write('%s\n' % public_ip_address[public_idx])

    def describe_instances(self, region_name, machines_name):
        client = boto3.client('ec2', region_name=region_name)
        is_spot_request = 'spotPrice' in self.protocol_config['CloudProviders']['aws']
        if is_spot_request:
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
        protocol_name = self.protocol_config['protocol']
        ready_instances = 0

        client = boto3.client('ec2', region_name=region)
        response = client.describe_instances()

        for res_idx in range(len(response['Reservations'])):
            reservations_len = len(response['Reservations'][res_idx]['Instances'])
            for reserve_idx in range(reservations_len):
                if response['Reservations'][res_idx]['Instances'][reserve_idx]['State']['Name'] == 'running' and \
                        response['Reservations'][res_idx]['Instances'][reserve_idx]['Tags'][0]['Value'] == \
                        protocol_name and \
                        response['Reservations'][res_idx]['Instances'][reserve_idx]['InstanceType'] == machine_type:
                    ready_instances += 1

        return ready_instances

    def start_instances(self):
        regions = self.protocol_config['CloudProviders']['aws']['regions']
        machines_name = self.protocol_config['protocol']

        for idx in range(len(regions)):
            region_name = regions[idx][:-1]
            instances = self.describe_instances(region_name, machines_name)

            client = boto3.client('ec2', region_name=region_name)
            client.start_instances(InstanceIds=instances)

    def stop_instances(self):
        regions = self.protocol_config['CloudProviders']['aws']['regions']
        machines_name = self.protocol_config['protocol']

        for idx in range(len(regions)):
            region_name = regions[idx][:-1]
            instances = self.describe_instances(region_name, machines_name)

            client = boto3.client('ec2', region_name=region_name)
            client.stop_instances(InstanceIds=instances)

    def change_instance_types(self):
        regions = self.protocol_config['CloudProviders']['aws']['regions']
        protocol_name = self.protocol_config['protocol']
        instance_type = self.protocol_config['aWSInstType']

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
                                                 Attribute='instanceType', Value=instance_type)

            # Start the instance
            client.start_instances(InstanceIds=instances)

    def terminate_instances(self):
        regions = self.protocol_config['CloudProviders']['aws']['regions']
        machines_name = self.protocol_config['protocol']

        for idx in range(len(regions)):
            region_name = regions[idx][:-1]

            instances = self.describe_instances(region_name, machines_name)

            client = boto3.client('ec2', region_name=region_name)
            client.terminate_instances(InstanceIds=instances)
