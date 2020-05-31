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

    def get_protocol_execution_data(self):
        protocol_name = self.protocol_config['protocolName']
        number_of_repetitions = int(self.protocol_config['numOfIterations'])
        configurations = self.protocol_config['configurations']
        working_directory = self.protocol_config['workingDirectory']
        executables = self.protocol_config['executableName']
        number_of_regions = len(self.protocol_config['cloudProviders'])
        return protocol_name, number_of_repetitions, configurations, working_directory, executables, number_of_regions

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

        protocol_name = self.protocol_config['protocolName']
        working_directory = self.protocol_config['workingDirectory']
        cp = list(self.protocol_config['cloudProviders'].keys())
        git_address = self.protocol_config['cloudProviders'][cp[0]]['git']['gitAddress']
        git_branch = self.protocol_config['cloudProviders'][cp[0]]['git']['gitBranch']
        git_address = git_address[0:8] + username + ':' + password + '@' + git_address[8:]

        os.makedirs('WebApp/ExecutionLogs', exist_ok=True)
        os.system(f'fab -f Execution/fabfile.py install_git_project:{git_address},{git_branch},'
                  f'{working_directory} --parallel | '
                  f' tee -a WebApp/ExecutionLogs/{protocol_name}.log')

    def execute_experiment(self):
        """
        Execute the protocol on remote servers
        """

        protocol_name, number_of_repetitions, configurations, working_directory, \
            executables, number_of_regions = self.get_protocol_execution_data()
        if 'coordinatorExecutable' in self.protocol_config:
            coordinator_executable = self.protocol_config['coordinatorExecutable']
            coordinator_args = self.protocol_config['coordinatorConfig']

        os.makedirs('WebApp/ExecutionLogs', exist_ok=True)
        for i in range(number_of_repetitions):
            for idx in range(len(configurations)):
                if 'coordinatorExecutable' in self.protocol_config:
                    os.system(f'fab -f Execution/fabfile.py run_protocol:{number_of_regions},'
                              f'{configurations[idx]},{executables},{working_directory}, '
                              f'{coordinator_executable},{coordinator_args} --parallel | '
                              f' tee -a WebApp/ExecutionLogs/{protocol_name}.log')
                else:
                    os.system(f'fab -f Execution/fabfile.py run_protocol:{number_of_regions},'
                              f'{configurations[idx]},{executables},{working_directory} --parallel | '
                              f' tee -a WebApp/ExecutionLogs/{protocol_name}.log')

    def execute_experiment_with_cpu_profiler(self):
        """
        Execute the protocol on remote servers with profiler.
        The first party is executed with profiler, the other executed normally
        """
        protocol_name, number_of_repetitions, configurations, working_directory, \
            executables, number_of_regions = self.get_protocol_execution_data()
        os.makedirs('WebApp/ExecutionLogs', exist_ok=True)

        for i in range(number_of_repetitions):
            for idx in range(len(configurations)):
                os.system(f'fab -f Execution/fabfile.py run_protocol_profiler:{number_of_regions},'
                          f'{configurations[idx]},{executables[idx]},{working_directory} --parallel | '
                          f' tee -a WebApp/ExecutionLogs/{protocol_name}.log')

    def execute_experiment_with_memory_profiler(self):
        """
        Execute the protocol on remote servers with profiler.
        The first party is executed with profiler, the other executed normally
        """
        protocol_name, number_of_repetitions, configurations, working_directory, \
            executables, number_of_regions = self.get_protocol_execution_data()

        for i in range(number_of_repetitions):
            for idx in range(len(configurations)):
                os.system(f'fab -f Execution/fabfile.py run_protocol_memory_profiler:{number_of_regions},'
                          f'{configurations[idx]},{executables[idx]},{working_directory} --parallel | '
                          f' tee -a WebApp/ExecutionLogs/{protocol_name}.log')

    def execute_experiment_with_latency(self):
        """
        Execute the protocol on remote servers with network latency
        """
        protocol_name, number_of_repetitions, configurations, working_directory, \
            executables, number_of_regions = self.get_protocol_execution_data()

        os.makedirs('WebApp/ExecutionLogs', exist_ok=True)
        for i in range(number_of_repetitions):
            for idx2 in range(len(configurations)):
                for idx in range(len(executables)):
                    os.system(f'fab -f Execution/fabfile.py run_protocol_with_latency::{number_of_regions},'
                              f'{configurations[idx2]},{executables[idx]},{working_directory[idx]} --parallel | '
                              f' tee -a WebApp/ExecutionLogs/{protocol_name}.log')

    def update_libscapi(self):
        """
        Update libscapi library on the remote servers from dev branch
        """
        protocol_name = self.protocol_config['protocolName']
        os.system('fab -f Execution/fabfile.py update_libscapi --parallel | '
                  f' tee -a WebApp/ExecutionLogs/{protocol_name}.log')

    def get_logs(self):
        """
        Copy logs file from remote servers
        """
        logs_directory = self.protocol_config['logs']
        protocol_name = self.protocol_config['protocolName']
        os.system(f'fab -f Execution/fabfile.py get_logs:{logs_directory} --parallel | '
                  f'tee -a WebApp/ExecutionLogs/{protocol_name}.log')

    def delete_old_experiment(self):
        protocol_name = self.protocol_config['protocolName']
        working_directory = self.protocol_config['workingDirectory']
        for idx in range(len(working_directory)):
            os.system(f'fab -f Execution/fabfile.py delete_old_experiment:{working_directory[idx]} --parallel | '
                      f'tee -a WebApp/ExecutionLogs/{protocol_name}.log')
