import boto3
import json

with open('instances_ids', 'r+') as ids_file:
    instances_ids = ids_file.readlines()


with open('config.json') as data_file:
        data = json.load(data_file)
        regions = list(data['regions'].values())

for idx in range(len(regions)):
    instances_ids = [x.strip() for x in instances_ids]
    client = boto3.client('ec2', region_name=regions[idx][:-1])
    response = client.terminate_instances(InstanceIds=instances_ids)
