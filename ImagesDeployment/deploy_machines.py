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


def deploy_instances():
    with open('config.json') as data_file:
        data = json.load(data_file)
        machine_type = data['AWS Instance Type']
        price_bids = data['AWS Pricing Bidding']
        number_of_parties = data['Number Of Parties']
        regions = list(data['Regions'].values())

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

    time.sleep(120)
    get_network_details()


def get_network_details():
    client = boto3.client('ec2')
    response = client.describe_spot_instance_requests()

    instances_ids = list()
    for req_idx in range(len(response['SpotInstanceRequests'])):
        instances_ids.append(response['SpotInstanceRequests'][req_idx]['InstanceId'])

    # save instance_ids for experiment termination
    with open('instances_ids', 'w+') as ids_file:
        for idx in range(len(instances_ids)):
            ids_file.write('%s\n' % instances_ids[idx])

    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    public_ip_address = list()
    private_ip_address = list()

    for inst in instances:
        public_ip_address.append(inst.public_ip_address)
        private_ip_address.append(inst.private_ip_address)

    # write public ips to file for fabric
    with open('public_ips', 'w+') as public_ip_file:
        for public_idx in range(len(public_ip_address)):
            public_ip_file.write('%s\n' % public_ip_address[public_idx])

    with open('parties.conf', 'w+') as private_ip_file:
        for private_idx in range(len(private_ip_address)):
            private_ip_file.write('party_%s_ip = %s\n' % (private_idx, private_ip_address[private_idx]))

        port_number = 8000

        for private_idx in range(len(private_ip_address)):
            private_ip_file.write('party_%s_port = %s\n' % (private_idx, port_number))


deploy_instances()

# create_security_group()
