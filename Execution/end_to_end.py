import os
import json


class E2E:
    """
    The class enables to execute protocols in the cloud or on premise
    Each server represents a different party
    """
    def __init__(self, protocol_config):
        """
        :type protocol_config str
        :param protocol_config: the configuration of the protocol we want to execute
        """
        self.protocol_config = protocol_config

    def install_experiment(self):
        """
        Install the protocol on remote servers
        """
        # read git credentials configuration
        try:
            with open('GlobalConfigurations/tokens.json', 'r') as tokens_file:
                data = json.load(tokens_file)
                username = data['GitHub']['user']
                password = data['GitHub']['password']

        except EnvironmentError:
            print('Cannot open tokens file')

        protocol_name = self.protocol_config['protocol']
        working_directory = self.protocol_config['workingDirectory']
        cp = list(self.protocol_config['CloudProviders'].keys())
        git_address = self.protocol_config['CloudProviders'][cp[0]]['git']['gitAddress']
        git_branch = self.protocol_config['CloudProviders'][cp[0]]['git']['gitBranch']

        for idx in range(len(working_directory)):
            os.system(f'fab -f Execution/fabfile.py install_git_project:{username},{password},{git_branch[idx]},'
                      f'{git_address[idx]},{working_directory[idx]} --parallel | '
                      f' tee WebApp/ExecutionLogs/{protocol_name}.log')

    def execute_experiment(self):
        """
        Execute the protocol on remote servers
        """
        protocol_name = self.protocol_config['protocol']
        number_of_repetitions = self.protocol_config['numOfRepetitions']
        configurations = self.protocol_config['configurations']
        working_directory = self.protocol_config['workingDirectory']
        executables = self.protocol_config['executableName']
        number_of_regions = len(self.protocol_config['CloudProviders'])
        if 'coordinatorExecutable' in self.protocol_config:
            coordinator_executable = self.protocol_config['coordinatorExecutable']
            coordinator_args = self.protocol_config['coordinatorConfig']

        for i in range(number_of_repetitions):
            for idx2 in range(len(configurations)):
                for idx in range(len(executables)):
                    if 'coordinatorExecutable' in self.protocol_config:
                        os.system(f'fab -f Execution/fabfile.py run_protocol:{number_of_regions},'
                                  f'{configurations[idx2]},{executables[idx]},{working_directory[idx]}, '
                                  f'{coordinator_executable}, {coordinator_args} --parallel | '
                                  f' tee WebApp/ExecutionLogs/{protocol_name}.log')
                    else:
                        os.system(f'fab -f Execution/fabfile.py run_protocol:{number_of_regions},'
                                  f'{configurations[idx2]},{executables[idx]},{working_directory[idx]},  --parallel | '
                                  f' tee WebApp/ExecutionLogs/{protocol_name}.log')

    def execute_experiment_callgrind(self):
        """
        Execute the protocol on remote servers with profiler.
        The first party is executed with profiler, the other executed normally
        """
        protocol_name = self.protocol_config['protocol']
        number_of_repetitions = self.protocol_config['numOfRepetitions']
        configurations = self.protocol_config['configurations']
        working_directory = self.protocol_config['workingDirectory']
        executables = self.protocol_config['executableName']
        number_of_regions = len(self.protocol_config['CloudProviders'])
        for i in range(number_of_repetitions):
            for idx2 in range(len(configurations)):
                for idx in range(len(executables)):
                    os.system(f'fab -f Execution/fabfile.py run_protocol_profiler:{number_of_regions},'
                              f'{configurations[idx2]},{executables[idx]},{working_directory[idx]} --parallel | '
                              f' tee WebApp/ExecutionLogs/{protocol_name}.log')

    def execute_experiment_with_latency(self):
        """
        Execute the protocol on remote servers with network latency
        """
        protocol_name = self.protocol_config['protocol']
        number_of_repetitions = self.protocol_config['numOfRepetitions']
        configurations = self.protocol_config['configurations']
        working_directory = self.protocol_config['workingDirectory']
        executables = self.protocol_config['executableName']
        number_of_regions = len(self.protocol_config['CloudProviders'])
        for i in range(number_of_repetitions):
            for idx2 in range(len(configurations)):
                for idx in range(len(executables)):
                    os.system(f'fab -f Execution/fabfile.py run_protocol_with_latency::{number_of_regions},'
                              f'{configurations[idx2]},{executables[idx]},{working_directory[idx]} --parallel | '
                              f' tee WebApp/ExecutionLogs/{protocol_name}.log')

    def update_libscapi(self):
        """
        Update libscapi library on the remote servers from dev branch
        """
        protocol_name = self.protocol_config['protocol']
        os.system('fab -f Execution/fabfile.py update_libscapi --parallel | '
                  f' tee WebApp/ExecutionLogs/{protocol_name}.log')

    def get_logs(self):
        """
        Copy logs file from remote servers
        """
        logs_directory = self.protocol_config['logs']
        protocol_name = self.protocol_config['protocol']
        os.system(f'fab -f Execution/fabfile.py get_logs:{logs_directory} --parallel | '
                  f'tee WebApp/ExecutionLogs/{protocol_name}.log')

    def delete_old_experiment(self):
        protocol_name = self.protocol_config['protocol']
        working_directory = self.protocol_config['workingDirectory']
        for idx in range(len(working_directory)):
            os.system(f'fab -f Execution/fabfile.py delete_old_experiment:{working_directory[idx]} --parallel | '
                      f'tee WebApp/ExecutionLogs/{protocol_name}.log')
