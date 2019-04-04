import os
import json


class E2E:
    """
    The class enables to execute protocols in the cloud or on premise
    Each server represents a different party
    """
    def __init__(self, protocol_config, protocol_config_path):
        """
        :type protocol_config str
        :param protocol_config: the configuration of the protocol we want to execute
        :type protocol_config_path str
        :param protocol_config_path: the path of the configuration file. Needed for Fabric
        """
        self.protocol_config = protocol_config
        self.protocol_config_path = protocol_config_path

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
        for i in range(number_of_repetitions):
            for idx2 in range(len(configurations)):
                for idx in range(len(executables)):
                    os.system(f'fab -f Execution/fabfile.py run_protocol:{self.protocol_config_path},'
                              f'{configurations[idx2]},{executables[idx]},{working_directory[idx]} --parallel | '
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
        for i in range(number_of_repetitions):
            for idx2 in range(len(configurations)):
                for idx in range(len(executables)):
                    os.system(f'fab -f Execution/fabfile.py run_protocol_profiler:{self.protocol_config_path},'
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
        for i in range(number_of_repetitions):
            for idx2 in range(len(configurations)):
                for idx in range(len(executables)):
                    os.system(f'fab -f Execution/fabfile.py run_protocol_with_latency:{self.protocol_config_path},'
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
                              f' tee WebApp/ExecutionLogs/{protocol_name}.log')
