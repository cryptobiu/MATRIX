import boto3
import json
import sys
import os

config_file_path = sys.argv[1]

with open(config_file_path) as data_file:
        data = json.load(data_file)
        regions = list(data['regions'].values())

for idx in range(len(regions)):
    with open('instances_ids_%s' % regions[idx][:-1], 'r+') as ids_file:
        instances_ids = ids_file.readlines()

    instances_ids = [x.strip() for x in instances_ids]
    client = boto3.client('ec2', region_name=regions[idx][:-1])
    response = client.terminate_instances(InstanceIds=instances_ids)
    os.remove('InstancesConfigurations/instances_ids_%s')

os.remove('InstancesConfigurations/public_ips*')
