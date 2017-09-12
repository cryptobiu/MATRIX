import os

import boto3
import json
import time


def create_security_group():
    client = boto3.client('ec2')
    response = client.create_security_group(
        Description='Matrix system security group',
        GroupName='MatrixSG',
        DryRun=False
    )
    print(response['GroupId'])


def create_instances():
    with open('config.json') as data_file:
        data = json.load(data_file)
        machine_type = data['AWS Instance Type']
        price_bids = data['AWS Pricing Bidding']
        network_type = data['Network']
        number_of_parties = data['Number Of Parties']
        conf = list(data['List of configurations'].values())
        regions = list(data['Regions'].values())
        print(conf)
        print(regions)

    if len(regions) > 1:
        number_of_instances = number_of_parties // len(regions)
    else:
        number_of_instances = number_of_parties

    client = boto3.client('ec2')

    for idx in range(len(regions)):
        client.request_spot_instances(
                DryRun=False,
                SpotPrice=price_bids,
                InstanceCount=number_of_instances,
                LaunchSpecification=
                {
                    'ImageId': 'ami-888f9df3',
                    'KeyName': 'matrix',
                    'SecurityGroupIds': ['sg-5f07f52c'],
                    'SecurityGroups': ['MatrixSG'],
                    'InstanceType': machine_type,
                    'Placement':
                        {
                            'AvailabilityZone': regions[idx],
                        },
                },
        )

    response = client.describe_spot_instance_requests()
    # wait until the request fulfilled
    time.sleep(120)

    instances_ids = list()
    for req_idx in range(len(response['SpotInstanceRequests'])):
        instances_ids.append(response['SpotInstanceRequests'][req_idx]['InstanceId'])

    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    # save instance_ids for experiment termination
    with open('instances_ids', 'w+') as ids_file:
        for idx in range(len(instances_ids)):
            ids_file.write('%s\n' % instances_ids[idx])

    for inst in instances:
        print(inst.public_ip_address)


create_instances()

# create_security_group()
