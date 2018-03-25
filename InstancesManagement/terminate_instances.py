import os
import boto3
import json
import glob


class Terminate:
    def __init__(self, conf_file):
        self.config_file_path = conf_file

    def terminate(self):
        with open(self.config_file_path) as data_file:
                data = json.load(data_file)
                regions = list(data['regions'].values())

        for idx in range(len(regions)):
            with open('InstancesConfigurations/instances_ids_%s' % regions[idx][:-1], 'r+') as ids_file:
                instances_ids = ids_file.readlines()

            instances_ids = [x.strip() for x in instances_ids]
            client = boto3.client('ec2', region_name=regions[idx][:-1])
            client.terminate_instances(InstanceIds=instances_ids)

        public_ips_files = glob.glob('InstancesConfigurations/public_ips*')
        if len(public_ips_files) > 0:
            for f in public_ips_files:
                try:
                    os.remove(f)
                except OSError:
                    pass

        instances_ids_files = glob.glob('InstancesConfigurations/instances_ids*')
        if len(instances_ids_files) > 0:
            for f in instances_ids_files:
                try:
                    os.remove(f)
                except OSError:
                    pass

