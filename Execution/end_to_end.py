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
        working_directory = list(self.protocol_config['workingDirectory'].values())
        external_protocol = self.protocol_config['isExternal']
        git_address = list(self.protocol_config['gitAddress'].values())
        git_branch = list(self.protocol_config['gitBranch'].values())

        for idx in range(len(working_directory)):
            os.system('fab -f Execution/fabfile.py install_git_project:%s,%s,%s,%s --parallel'
                      % (git_branch[idx], working_directory[idx], git_address[idx], external_protocol))

    def execute_experiment(self):
        number_of_repetitions = self.protocol_config['numOfRepetitions']
        configurations = list(self.protocol_config['configurations'].values())
        for i in range(number_of_repetitions):
            for idx in range(len(configurations)):
                os.system('fab -f Execution/fabfile.py run_protocol:%s,%s --parallel'
                          % (self.protocol_config_path, configurations[idx]))
                with open('Execution/execution_log.log', 'a+') as log_file:
                    log_file.write('%s\n' % configurations[idx])

    def execute_experiment_callgrind(self):
        number_of_repetitions = self.protocol_config['numOfRepetitions']
        configurations = list(self.protocol_config['configurations'].values())
        for i in range(number_of_repetitions):
            for idx in range(len(configurations)):
                os.system('fab -f Execution/fabfile.py run_protocol_profiler:%s,%s --parallel'
                          % (self.protocol_config_path, configurations[idx]))
                with open('Execution/execution_log.log', 'a+') as log_file:
                    log_file.write('%s\n' % configurations[idx])

    @staticmethod
    def update_libscapi():
        branch = input('Enter libscapi branch to update from:')
        os.system('fab -f Execution/fabfile.py update_libscapi:%s --parallel' % branch)

    def check_if_poll_completed(self):
        pass
