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
        os.system('fab -f ExperimentExecute/fabfile.py pre_process:%s,%s --parallel --no-pty'
                  % (working_directory, pre_process_task))

    def install_experiment(self):
        with open(self.config_file_path) as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)

        working_directory = data['workingDirectory']
        external_protocol = data['isExternal']

        if external_protocol == 'True':
            install_script = data['installScript']
            os.system('fab -f ExperimentExecute/fabfile.py install_git_project:%s,%s,%s,%s,%s --parallel --no-pty'
                      % ('', working_directory, '', external_protocol, install_script))
        else:
            git_address = data['gitAddress']
            git_branch = data['gitBranch']
            os.system('fab -f ExperimentExecute/fabfile.py install_git_project:%s,%s,%s,%s,%s --parallel --no-pty'
                      % (git_branch, working_directory, git_address, external_protocol, ''))

    def execute_experiment(self):
        with open(self.config_file_path) as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)

        number_of_repetitions = data['numOfRepetitions']
        configurations = list(data['configurations'].values())
        for i in range(number_of_repetitions):
            for idx in range(len(configurations)):
                os.system('fab -f ExperimentExecute/fabfile.py run_protocol:%s,%s --parallel --no-pty'
                          % (self.config_file_path, configurations[idx]))

    @staticmethod
    def update_libscapi():
        branch = input('Enter libscapi branch to update from:')
        os.system('fab -f ExperimentExecute/fabfile.py update_libscapi:%s --parallel --no-pty' % branch)

    def check_if_poll_completed(self):
        pass