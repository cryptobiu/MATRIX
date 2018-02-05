import os
import sys
import boto3
import botocore
import json
import time
import copy
from random import shuffle
from datetime import datetime
from collections import OrderedDict
from botocore import exceptions


config_file_path = sys.argv[1]
task_idx = sys.argv[2]


def create_key_pair():
    with open(config_file_path) as regions_file:
        data = json.load(regions_file, object_pairs_hook=OrderedDict)
        regions = list(data['regions'].values())

    for idx in range(len(regions)):
        client = boto3.client('ec2', region_name=regions[idx][:-1])
        try:
            key_pair = client.create_key_pair(KeyName='Matrix%s' % regions[idx].replace('-', '')[:-1])
            print('Key value for : %s' % key_pair['KeyName'])
            print(key_pair['KeyMaterial'])
            print()
        except botocore.exceptions.EndpointConnectionError as e:
            print(e.response['Error']['Message'].upper())
        except botocore.exceptions.ClientError as e:
            print(e.response['Error']['Message'].upper())


def create_security_group():
    with open(config_file_path) as regions_file:
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


def check_latest_price(instance_type, region):
    client = boto3.client('ec2', region_name=region[:-1])
    prices = client.describe_spot_price_history(InstanceTypes=[instance_type], MaxResults=1,
                                                ProductDescriptions=['Linux/UNIX (Amazon VPC)'],
                                                AvailabilityZone=region)
    return prices['SpotPriceHistory'][0]['SpotPrice']


def deploy_instances():
    with open(config_file_path) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
        machine_type = data['aWSInstType']
        price_bids = data['aWWSBidPrice']
        number_of_parties = list(data['numOfParties'].values())
        amis_id = list(data['amis'].values())
        regions = list(data['regions'].values())
        number_duplicated_servers = 0
        spot_request = data['isSpotRequest']

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

        number_of_instances_to_deploy = check_running_instances(regions[idx][:-1], machine_type)
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
                winning_bid_price = check_latest_price(machine_type, regions[idx])
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
                                'KeyName': 'Matrix%s' % regions[idx].replace('-', '')[:-1],
                                'SecurityGroups': ['MatrixSG%s' % regions[idx].replace('-', '')[:-1]],
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
                    KeyName='Matrix%s' % regions[idx].replace('-', '')[:-1],
                    MinCount=int(number_of_instances_to_deploy),
                    MaxCount=int(number_of_instances_to_deploy),
                    SecurityGroups=['MatrixSG%s' % regions[idx].replace('-', '')[:-1]],
                    InstanceType=machine_type,
                    Placement=
                    {
                        'AvailabilityZone': regions[idx],
                    }
                )

    print('Waiting for the images to be deployed..')
    time.sleep(240)
    get_network_details()

    print('Finished to deploy machines')


def create_parties_files_multi_regions():
    with open('InstancesConfigurations/parties.conf', 'r') as origin_file:
        parties = origin_file.readlines()

    number_of_parties = len(parties) // 2

    for idx in range(number_of_parties):
        new_parties = copy.deepcopy(parties)
        new_parties[idx] = 'party_%s_ip=0.0.0.0\n' % idx

        # write data to file
        with open('InstancesConfigurations/parties%s.conf' % idx, 'w+') as new_file:
            new_file.writelines(new_parties)


def get_aws_network_details():
    with open(config_file_path) as data_file:
        data = json.load(data_file)
        regions = list(data['regions'].values())

    instances_ids = []
    public_ip_address = []

    if len(regions) == 1:
        private_ip_address = []

    # get the spot instances ids
    for idx in range(len(regions)):
        client = boto3.client('ec2', region_name=regions[idx][:-1])
        response = client.describe_spot_instance_requests()

        for req_idx in range(len(response['SpotInstanceRequests'])):
            if response['SpotInstanceRequests'][req_idx]['State'] == 'active' or \
                            response['SpotInstanceRequests'][req_idx]['State'] == 'open':
                instances_ids.append(response['SpotInstanceRequests'][req_idx]['InstanceId'])

        # save instance_ids for experiment termination
        with open('InstancesConfigurations/instances_ids_%s' % regions[idx][:-1], 'a+') as ids_file:
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
    with open('InstancesConfigurations/parties.conf', 'w+') as private_ip_file:
        if len(regions) > 1:
            for public_idx in range(len(public_ip_address)):
                print('party_%s_ip=%s' % (public_idx, public_ip_address[public_idx]))
                private_ip_file.write('party_%s_ip=%s\n' % (public_idx, public_ip_address[public_idx]))
        else:
            for private_idx in range(len(private_ip_address)):
                print('party_%s_ip=%s' % (private_idx, private_ip_address[private_idx]))
                private_ip_file.write('party_%s_ip=%s\n' % (private_idx, private_ip_address[private_idx]))

        port_number = 8000

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
        create_parties_files_multi_regions()


def get_network_details():
    with open(config_file_path) as data_file:
        data = json.load(data_file)
        regions = list(data['regions'].values())

    public_ip_address = []

    number_of_parties = max(list(data['numOfParties'].values()))
    if 'local' in regions:
        with open('InstancesConfigurations/parties.conf', 'w+') as private_ip_file:
            for ip_idx in range(len(number_of_parties)):
                private_ip_file.write('party_%s_ip=127.0.0.1\n' % ip_idx)
                public_ip_address.append('127.0.0.1')

            port_counter = 8000
            for ip_idx in range(len(number_of_parties)):
                private_ip_file.write('party_%s_port=%s\n' % (ip_idx, port_counter))
                port_counter += 100

    elif 'servers' in regions:
        server_file = input('Enter your server file configuration: ')
        os.system('mv %s InstancesConfigurations/public_ips' % server_file)

        server_ips = []
        with open('InstancesConfigurations/public_ips', 'r+') as server_ips_file:
            for line in server_ips_file:
                server_ips.append(line)

            with open('InstancesConfigurations/parties.conf', 'w+') as private_ip_file:
                for ip_idx in range(len(server_ips)):
                    print('party_%s_ip=%s' % (ip_idx, server_ips[ip_idx]))
                    private_ip_file.write('party_%s_ip=127.0.0.1' % ip_idx)

                port_counter = 8000
                for ip_idx in range(len(server_ips)):
                    private_ip_file.write('party_%s_port=%s\n' % (ip_idx, port_counter))
    else:
        get_aws_network_details()


def check_running_instances(region, machine_type):

    instances_ids = list()
    instances_count = 0

    client = boto3.client('ec2', region_name=region)
    response = client.describe_spot_instance_requests()

    for req_idx in range(len(response['SpotInstanceRequests'])):
        if (response['SpotInstanceRequests'][req_idx]['State'] == 'active' or \
                        response['SpotInstanceRequests'][req_idx]['State'] == 'open')\
                and response['SpotInstanceRequests'][req_idx]['LaunchSpecification']['InstanceType'] == machine_type:
            instances_ids.append(response['SpotInstanceRequests'][req_idx]['InstanceId'])

    ec2 = boto3.resource('ec2', region_name=region)
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    for inst in instances:
        if inst.id in instances_ids:
            instances_count += 1

    return instances_count


if task_idx == '1':
    deploy_instances()
elif task_idx == '2':
    create_key_pair()
elif task_idx == '3':
    create_security_group()
elif task_idx == '4':
    get_network_details()
else:
    raise ValueError('Invalid choice')
