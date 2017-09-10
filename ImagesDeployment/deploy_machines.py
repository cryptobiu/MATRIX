import boto3
import json
from pprint import pprint


with open('config.json') as data_file:
    data = json.load(data_file)
    machine_type = data['AWS Instance Type']
    price_bids = data['AWS Pricing Bidding']
    request_time = data['ExecRequestTime']
    is_published = data['IsPublished']
    network_type = data['Network']
    number_of_parties = data['Number Of Parties']
    number_of_repitions = data['Number of Repetitions']
    protocol = data['Protocol']
    commit_id = data['Git commit id']
    git_branch = data['Git Branch']

pprint(data)

client = boto3.client('ec2')
ec2 = boto3.resource('ec2')
# response = client.request_spot_instances(
#         DryRun=False,
#         SpotPrice=price_bids,
#         InstanceCount=number_of_parties,
#         LaunchSpecification=
#         {
#             'ImageId': 'ami-888f9df3',
#             'KeyName': 'matrix',
#             'InstanceType': 'm4.large',
#             'Placement':
#                 {
#                     'AvailabilityZone': 'us-east-1b',
#                 },
#         },
#     )
response = client.describe_spot_instance_requests()
print(response['SpotInstanceRequests'])
print(type(response['SpotInstanceRequests']))

instances_ids = list()
for req_idx in range(len(response['SpotInstanceRequests'])):
    print(response['SpotInstanceRequests'][req_idx]['InstanceId'])
    instances_ids.append(response['SpotInstanceRequests'][req_idx]['InstanceId'])


instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

for inst in instances:
    print(inst.public_ip_address)
