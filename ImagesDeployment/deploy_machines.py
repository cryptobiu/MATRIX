import os
import sys
import boto3
import json
import time
from datetime import datetime
from collections import OrderedDict


config_file_path = sys.argv[1]


def create_key_pair():
    with open(config_file_path) as regions_file:
        regions = list(regions_file['regions'].values())

    for region in regions:
        ec2 = boto3.resource('ec2', region_name=region)
        keypair = ec2.create_key_pair(KeyName='Matrix%s' % region.replace('-', ''))
        print(keypair.key_material)


def create_security_group():
    with open(config_file_path) as regions_file:
        regions = list(regions_file['regions'].values())

    for region in regions:
        client = boto3.client('ec2', region_name=region)
        response = client.create_security_group(
            Description='Matrix system security group',
            GroupName='MatrixSG%s' % region.replace('-', ''),
            DryRun=False
        )
        sg_id = response['GroupId']
        ec2 = boto3.resource('ec2', region_name=region)
        security_group = ec2.SecurityGroup(sg_id)
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=0, ToPort=65535)


def deploy_instances():
    with open(config_file_path) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
        machine_type = data['aWSInstType']
        price_bids = data['aWWSBidPrice']
        number_of_parties = list(data['numOfParties'].values())
        amis_id = list(data['amis'].values())
        regions = list(data['regions'].values())

    if len(regions) > 1:
        number_of_instances = max(number_of_parties) // len(regions)
    else:
        number_of_instances = max(number_of_parties)

    date = datetime.now().replace(hour=datetime.now().hour - 3)
    print('Current date : \n %s' % str(date))
    new_date = date.replace(hour=date.hour + 6)

    for idx in range(len(regions)):
        client = boto3.client('ec2', region_name=regions[idx][:-1])

        print('Deploying instances :\n region : %s\n number of instances : %s\n  ami_id : %s\n instance_type : %s\n '
              'valid until : %s' % (regions[idx], number_of_instances, amis_id[idx], machine_type, str(new_date)))

    #     client.request_spot_instances(
    #             DryRun=False,
    #             SpotPrice=price_bids,
    #             InstanceCount=number_of_instances,
    #             LaunchSpecification=
    #             {
    #                 'ImageId': amis_id[idx],
    #                 'KeyName': 'Matrix%s' % regions[idx].replace('-', '')[:-1],
    #                 'SecurityGroups': ['MatrixSG%s' % regions[idx].replace('-', '')[:-1]],
    #                 'InstanceType': machine_type,
    #                 'Placement':
    #                     {
    #                         'AvailabilityZone': regions[idx],
    #                     },
    #             },
    #             ValidUntil=new_date
    #     )
    #
    # time.sleep(240)

    get_network_details(regions)
    print('Finished to deploy machines')
    sys.stdout.flush()


def get_network_details(regions):
    with open(config_file_path) as data_file:
        data = json.load(data_file)
        protocol_name = data['protocol']
        os.system('mkdir -p ../%s' % protocol_name)

    instances_ids = list()
    public_ip_address = list()

    if len(regions) == 1:
        private_ip_address = list()

    for idx in range(len(regions)):
        client = boto3.client('ec2', region_name=regions[idx][:-1])
        response = client.describe_spot_instance_requests()

        for req_idx in range(len(response['SpotInstanceRequests'])):
            instances_ids.append(response['SpotInstanceRequests'][req_idx]['InstanceId'])

        # save instance_ids for experiment termination
        with open('instances_ids', 'w+') as ids_file:
            for instance_idx in range(len(instances_ids)):
                ids_file.write('%s\n' % instances_ids[instance_idx])

            ec2 = boto3.resource('ec2', region_name=regions[idx][:-1])
            instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

            counter = 0
            number_of_instances = len(response['SpotInstanceRequests'])

            for inst in instances:
                if counter >= number_of_instances:
                    break

                public_ip_address.append(inst.public_ip_address)
                if len(regions) == 1:
                    private_ip_address.append(inst.private_ip_address)
                counter += 1

        # write public ips to file for fabric
        with open('public_ips', 'w+') as public_ip_file:
            for public_idx in range(len(public_ip_address)):
                public_ip_file.write('%s\n' % public_ip_address[public_idx])

        print('Parties network configuration')
        with open('parties.conf', 'w+') as private_ip_file:
            if len(regions) > 1:
                for private_idx in range(len(public_ip_address)):
                    print('party_%s_ip = %s' % (private_idx, public_ip_address[private_idx]))
                    private_ip_file.write('party_%s_ip = %s\n' % (private_idx, public_ip_address[private_idx]))
            else:
                for private_idx in range(len(private_ip_address)):
                    print('party_%s_ip = %s' % (private_idx, private_ip_address[private_idx]))
                    private_ip_file.write('party_%s_ip = %s\n' % (private_idx, private_ip_address[private_idx]))

            port_number = 8000

            for private_idx in range(len(public_ip_address)):
                print('party_%s_port = %s' % (private_idx, port_number))
                private_ip_file.write('party_%s_port = %s\n' % (private_idx, port_number))


deploy_instances()
