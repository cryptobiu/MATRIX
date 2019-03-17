import os
import glob

from Deployment import aws_deploy as awsde
from Deployment import azure_deploy as ade


class MultiCP:
    """
    The class enables deployment to two cloud providers at the same time:
        1. AWS
        2. Azure
    """
    def __init__(self, protocol_config):
        """
        Init  instances of Deployment.AmazonCP and Deployment.AzureCP
        :type protocol_config str
        :param protocol_config: the configuration of the protocol we want to deploy
        """
        self.aws = awsde.AmazonCP(protocol_config)
        self.azure = ade.AzureCP(protocol_config)

    def deploy_instances(self):
        """
        Deploy instances at AWS and Azure
        :return:
        """
        self.aws.deploy_instances()
        self.azure.deploy_instances()

    def start_instances(self):
        """
        Turn on the instances
        """
        self.aws.start_instances()
        self.azure.start_instances()

    def stop_instances(self):
        """
        Shut down the instances
        """
        self.aws.stop_instances()
        self.azure.stop_instances()

    def terminate_instances(self):
        """
        Deletes the instances
        """
        self.aws.terminate_instances()
        self.azure.terminate_instances()

        try:
            cwd = os.getcwd()
            parties_file = glob.glob('%s/InstancesConfigurations/parties*.conf' % cwd)
            for file in parties_file:
                os.remove(file)
            os.remove('%s/InstancesConfigurations/public_ips' % cwd)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

    def get_network_details(self):
        """
        Creates party file for all the parties
        """
        self.aws.get_network_details()
        self.azure.get_network_details()

        file_path = f'{os.getcwd()}/InstancesConfigurations/parties.conf'

        try:
            with open(file_path, 'r+') as parties_file:
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
        except EnvironmentError:
            print(f'Cannot write to {file_path}')

        self.aws.create_parties_files_multi_regions('parties.conf')

