import boto3
import json
from InstancesManagement import deploy_instances


class Terminate:
    def __init__(self, conf_file):
        self.config_file_path = conf_file

    def terminate(self):
        with open(self.config_file_path) as data_file:
            data = json.load(data_file)
            regions = list(data['regions'].values())
            machines_name = data['protocol']

        for idx in range(len(regions)):
            region_name = regions[idx][:-1]

            instances = deploy_instances.Deploy.describe_instances(region_name, machines_name)

            client = boto3.client('ec2', region_name=region_name)
            client.terminate_instances(InstanceIds=instances)
