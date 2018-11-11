import os
import glob

from Deployment import aws_deploy as awsde
from Deployment import scaleway_deploy as sde


class MultiCP:
    def __init__(self, protocol_config):
        self.aws = awsde.AmazonCP(protocol_config)
        self.scaleway = sde.ScalewayCP(protocol_config)

    def deploy_instances(self):
        self.aws.deploy_instances()
        self.scaleway.deploy_instances()

    def start_instances(self):
        self.aws.start_instances()
        self.scaleway.start_instances()

    def stop_instances(self):
        self.aws.stop_instances()
        self.scaleway.stop_instances()

    def terminate_instances(self):
        self.aws.terminate_instances()
        self.scaleway.terminate_instances()

        try:
            cwd = os.getcwd()
            parties_file = glob.glob('%s/InstancesConfigurations/parties*.conf' % cwd)
            for file in parties_file:
                os.remove(file)
            os.remove('%s/InstancesConfigurations/public_ips' % cwd)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

    def get_network_details(self):
        self.aws.get_network_details()
        self.scaleway.get_network_details()

        with open('%s/InstancesConfigurations/parties.conf' % os.getcwd(), 'r+') as parties_file:
            parties = []
            origin_data = parties_file.readlines()
            for d in origin_data:
                if 'ip' in d:
                    # get the ip address
                    parties.append(d.split('=')[1])

            parties_file.seek(0)
            for idx in range(len(parties)):
                parties_file.write('party_%s_ip=%s' % (idx, parties[idx]))

            for idx in range(len(parties)):
                parties_file.write('party_%s_port=8000\n' % idx)

            parties_file.truncate()

        self.aws.create_parties_files_multi_regions('parties.conf')

