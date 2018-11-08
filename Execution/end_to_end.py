import os
import json
from collections import OrderedDict


class E2E:
    def __init__(self, protocol_config, protocol_config_path):
        self.protocol_config = protocol_config
        self.protocol_config_path = protocol_config_path

    def pre_process(self):
        working_directory = self.protocol_config['workingDirectory']
        pre_process_task = self.protocol_config['preProcessTask']
        os.system('fab -f Execution/fabfile.py pre_process:%s,%s --parallel'
                  % (working_directory, pre_process_task))

    def install_experiment(self):
        working_directory = self.protocol_config['workingDirectory']
        external_protocol = json.loads(self.protocol_config['isExternal'])
        cloud_providers = self.protocol_config['CloudProviders']
        #
        # THIS IS REALLY HACKY. Probably git-info should not be given on a per cloud provider basis
        #
        assert len(cloud_providers.keys()) > 0
        provider = list(cloud_providers.keys())[0]
        git_address = cloud_providers[provider]['git']['gitAddress']
        git_branch = cloud_providers[provider]['git']['gitBranch']
        
        for idx in range(len(working_directory)):
            os.system('fab -f Execution/fabfile.py install_git_project:%s,%s,%s,%s'
                      % (git_branch[idx], working_directory[idx], git_address[idx], external_protocol))

    def execute_experiment(self):
        number_of_repetitions = self.protocol_config['numOfRepetitions']
        configurations = self.protocol_config['configurations']
        working_directory = self.protocol_config['workingDirectory']
        executables = self.protocol_config['executableName']
        for i in range(number_of_repetitions):
            for idx2 in range(len(configurations)):
                for idx in range(len(executables)):
                    os.system('fab -f Execution/fabfile.py run_protocol:%s,%s,%s,%s --parallel'
                              % (self.protocol_config_path, configurations[idx2],
                                 executables[idx], working_directory[idx]))

    def execute_experiment_callgrind(self):
        number_of_repetitions = self.protocol_config['numOfRepetitions']
        configurations = self.protocol_config['configurations']
        working_directory = self.protocol_config['workingDirectory']
        executables = self.protocol_config['executableName']
        for i in range(number_of_repetitions):
            for idx2 in range(len(configurations)):
                for idx in range(len(executables)):
                    os.system('fab -f Execution/fabfile.py run_protocol_profiler:%s,%s,%s,%s --parallel'
                              % (self.protocol_config_path, configurations[idx2],
                                 executables[idx], working_directory[idx]))

    @staticmethod
    def update_libscapi():
        branch = input('Enter libscapi branch to update from:')
        os.system('fab -f Execution/fabfile.py update_libscapi:%s --parallel' % branch)

    def check_if_poll_completed(self):
        pass
