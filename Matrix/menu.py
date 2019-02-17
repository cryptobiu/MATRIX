import json
import math
import os
import colorama
from collections import OrderedDict
from Deployment import deploy as de
from Deployment import aws_deploy as awsde
from Deployment import scaleway_deploy as sde
from Deployment import multi_cp_deploy as mde
from Execution import end_to_end as e2e
from Reporting import analyze_results as ar
from Reporting import upload_elastic as ue


class MatrixMenu:
    """
    Class handling the command line menu of the Matrix client.  Use the run()
    method to start the menu.
    """

    d = {'blue': colorama.Fore.CYAN,
         'green': colorama.Fore.GREEN,
         'yellow': colorama.Fore.YELLOW,
         'red': colorama.Fore.RED,
         'magenta': colorama.Fore.MAGENTA}

    main_menu_desc = (
        'Welcome to MATRIX system.\nPlease Insert your choice:',
        [
            'Deploy Menu',
            'Execute Menu',
            'Analysis Menu',
            'Generate Circuits',
            'Change Protocol Configuration',
            'Exit',
        ],
        'blue')

    cloud_provider_menu_desc = (
        'Choose cloud provider',
        ['AWS', 'Scaleway', 'Both', 'Local', 'Servers', 'Return'],
        'blue')

    deploy_menu_desc = (
        'Choose deployment task',
        [
            'Deploy Instance(s)',
            'Create Key pair(s)',
            'Create security group(s)',
            'Get instances network data',
            'Terminate machines',
            'Change machines types',
            'Start instances',
            'Stop instances',
            'Copy AMI',
            'Return',
        ])

    execution_menu_desc = (
        'Choose task to be executed:',
        [
            'Preform pre process operations',
            'Install Experiment',
            'Execute Experiment',
            'Execute Experiment with profiler',
            'Execute Experiment with latency',
            'Update libscapi',
            'Return',
        ],
        'yellow')

    analysis_menu_desc = (
        'Choose analysis task to be executed:',
        [
            'Download & Analyze Results',
            'Download Results',
            'Analyze Results',
            'Upload data to Elasticsearch',
            'Return',
        ],
        'green')

    def __init__(self):
        self.protocol_config = None
        self.protocol_config_path = None

    @staticmethod
    def color_print(text, color):
        """
        Print text in given color and reset coloring afterwards.
        """
        color_code = MatrixMenu.d[color]
        reset_code = colorama.Fore.RESET
        print(''.join([color_code, text, reset_code]))

    @staticmethod
    def color_input(prompt, color):
        """
        Read from stdin with a colored prompt.
        """
        color_code = MatrixMenu.d[color]
        reset_code = colorama.Fore.RESET
        return input(''.join([color_code, prompt, reset_code]))

    @staticmethod
    def read_number(maximum, color, prompt='Your choice: '):
        """
        Read a number in the range [1, maximum] from stdin and return the
        integer.
        """
        while True:
            choice = MatrixMenu.color_input(prompt, color).strip()
            if not choice.isdecimal():
                MatrixMenu.color_print('Please enter a number from 1 to {}'.format(maximum), color)
                continue
            choice = int(choice)
            if not 1 <= choice <= maximum:
                MatrixMenu.color_print('Please enter a number from 1 to {}'.format(maximum), color)
                continue
            return choice

    @staticmethod
    def print_menu(title, items, color):
        """
        Print menu in given color and return index of selected element.  In
        case of EOF, the last element (usually exit or return) is selected.
        """
        MatrixMenu.color_print(title, color)
        num_items = len(items)
        width = math.floor(math.log10(num_items))
        for i, item in enumerate(items, 1):
            MatrixMenu.color_print('{i:{width}d}. {item}'.format(i=i, width=width, item=item), color)
        try:
            choice = MatrixMenu.read_number(num_items, color)
        except EOFError:
            choice = num_items
        return choice

    def run(self, config_path=None):
        """
        Start the client.
        """
        try:
            while self.protocol_config is None:
                self.load_protocol_config(config_path)
            self.main_menu()
        except KeyboardInterrupt:
            print('\nReceived KeyboardInterrupt, quitting ...')

    def load_protocol_config(self, protocol_config_path=None):
        """
        Read relative path of a protocol configuration file.
        """
        if (protocol_config_path == None):
            self.color_print('Enter configuration file(s):', 'blue')
            cwd = os.getcwd()
            prompt = 'Protocol configuration file path (current path is: {}): '.format(cwd)
            try:
                protocol_config_path = self.color_input(prompt,  'blue')
            except EOFError:
                return
        try:
            with open(protocol_config_path, 'r') as f:
                self.protocol_config = json.load(f, object_pairs_hook=OrderedDict)
        except json.decoder.JSONDecodeError as e:
            MatrixMenu.color_print("Configuration file '{}' is not valid".format(protocol_config_path), 'blue')
            return
        except OSError as e:
            MatrixMenu.color_print("Reading config file '{}' failed: {}".format(e.filename, e.strerror), 'blue')
            return
        self.protocol_config_path = protocol_config_path

    def main_menu(self):
        """
        Show main menu.
        """
        selection = self.print_menu(*self.main_menu_desc)
        while not selection == 6:

            if selection == 1:
                self.instances_management_menu()
            elif selection == 2:
                self.execution_menu()
            elif selection == 3:
                self.analysis_menu()
            elif selection == 4:
                de.DeployCP.generate_circuits()
            elif selection == 5:
                self.load_protocol_config()

            selection = self.print_menu(*self.main_menu_desc)

    def instances_management_menu(self):
        """
        Show instances management menu.
        """
        cp = self.print_menu(*self.cloud_provider_menu_desc)
        if cp == 1:
            deploy = awsde.AmazonCP(self.protocol_config)
            menu_color = 'red'
        elif cp == 2:
            deploy = sde.ScalewayCP(self.protocol_config)
            menu_color = 'magenta'
        elif cp == 3:
            deploy = mde.MultiCP(self.protocol_config)
            menu_color = 'blue'
        elif cp == 4 or cp == 5:
            deploy = de.DeployCP(self.protocol_config)
            menu_color = 'blue'
        else:
            return

        selection = self.print_menu(*self.deploy_menu_desc, menu_color)

        try:
            if selection == 1:
                deploy.deploy_instances()
            elif selection == 2:
                deploy.create_key_pair()
            elif selection == 3:
                deploy.create_security_group()
            elif selection == 4:
                deploy.get_network_details()
            elif selection == 5:
                deploy.terminate_instances()
            elif selection == 6:
                deploy.change_instance_types()
            elif selection == 7:
                deploy.start_instances()
            elif selection == 8:
                deploy.stop_instances()
            elif selection == 9:
                deploy.copy_ami()
        except NotImplementedError:
            MatrixMenu.color_print("Selected action '{}' is not implemented for the chosen deployment '{}'".format(self.deploy_menu_desc[1][selection - 1], self.cloud_provider_menu_desc[1][cp - 1]), menu_color)
            self.instances_management_menu()

    def execution_menu(self):
        """
        Show execution menu.
        """
        selection = self.print_menu(*self.execution_menu_desc)

        ee = e2e.E2E(self.protocol_config, self.protocol_config_path)

        if selection == 1:
            ee.pre_process()
        elif selection == 2:
            ee.install_experiment()
        elif selection == 3:
            ee.execute_experiment()
        elif selection == 4:
            ee.execute_experiment_callgrind()
        elif selection == 5:
            ee.execute_experiment_with_latency()
        elif selection == 6:
            ee.update_libscapi()

    def analysis_menu(self):
        """
        Show analysis menu.
        """
        selection = self.print_menu(*self.analysis_menu_desc)

        a = ar.Analyze(self.protocol_config)

        if selection == 1:
            a.download_data()
            a.analyze_results()
        elif selection == 2:
            a.download_data()
        elif selection == 3:
            a.analyze_results()
        elif selection == 4:
            e = ue.Elastic(self.protocol_config)
            e.upload_all_data()
