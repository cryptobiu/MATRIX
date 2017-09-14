import boto3

with open('instances_ids', 'r+') as ids_file:
    instances_ids = ids_file.readlines()

instances_ids = [x.strip() for x in instances_ids]
client = boto3.client('ec2')
response = client.terminate_instances(InstanceIds=instances_ids)
