import os
import json
from collections import OrderedDict


class E2E:
    def __init__(self, conf_file):
        self.config_file_path = conf_file

    def pre_process(self):
        with open(self.config_file_path) as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)
        working_directory = data['workingDirectory']
        pre_process_task = data['preProcessTask']
        os.system('fab -f Execution/fabfile.py pre_process:%s,%s --parallel --no-pty'
                  % (working_directory, pre_process_task))

    def install_experiment(self):
        with open(self.config_file_path) as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)

        working_directory = list(data['workingDirectory'].values())
        external_protocol = data['isExternal']
        git_address = list(data['gitAddress'].values())
        git_branch = list(data['gitBranch'].values())

        for idx in range(len(working_directory)):
            os.system('fab -f Execution/fabfile.py install_git_project:%s,%s,%s,%s --parallel --no-pty'
                      % (git_branch[idx], working_directory[idx], git_address[idx], external_protocol))

    def execute_experiment(self):
        with open(self.config_file_path) as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)

        number_of_repetitions = data['numOfRepetitions']
        configurations = list(data['configurations'].values())
        for i in range(number_of_repetitions):
            for idx in range(len(configurations)):
                os.system('fab -f Execution/fabfile.py run_protocol:%s,%s --parallel --no-pty'
                          % (self.config_file_path, configurations[idx]))
                with open('Execution/execution_log.log', 'a+') as log_file:
                    log_file.write('%s\n' % configurations[idx])

    @staticmethod
    def update_libscapi():
        branch = input('Enter libscapi branch to update from:')
        os.system('fab -f Execution/fabfile.py update_libscapi:%s --parallel --no-pty' % branch)

    def check_if_poll_completed(self):
        pass