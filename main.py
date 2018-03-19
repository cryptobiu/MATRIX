import os
import colorama
from InstancesManagement import deploy_instances as di
from InstancesManagement import terminate_instances as ti
from ExperimentExecute import end_to_end as e2e
from ExperimentReport import analyze_results as ar
from ExperimentReport import upload_elastic as ue

d = {'blue': colorama.Fore.BLUE,
     'green': colorama.Fore.GREEN,
     'yellow': colorama.Fore.YELLOW,
     'red': colorama.Fore.RED}


def color_print(text, color):
    c = d[color]
    print('{}{}'.format(c, text))


def print_main_menu():
    color_print('Welcome to MATRIX system.\nPlease Insert your choice:', 'blue')
    color_print('1. Deploy Menu', 'blue')
    color_print('2. Execute Menu', 'blue')
    color_print('3. Analysis Menu', 'blue')
    color_print('4. Exit', 'blue')
    selection = input('Your choice:')
    return selection


def print_instances_management_menu(conf_file_path):
    color_print('Choose deployment task', 'red')
    color_print('1. Deploy Instance(s)', 'red')
    color_print('2. Create Key pair(s)', 'red')
    color_print('3. Create security group(s)', 'red')
    color_print('4. Get instances network data', 'red')
    color_print('5. Terminate Machines', 'red')
    selection = input('Your choice:')

    di.config_file_path = conf_file_path

    if selection == '1':
        di.deploy_instances()
    elif selection == '2':
        di.create_key_pair()
    elif selection == '3':
        di.create_security_group()
    elif selection == '4':
        di.get_network_details()
    elif selection == '5':
        ti.config_file_path = conf_file_path
        ti.main()


def print_execution_menu(conf_file_path):
    color_print('Choose task to be executed:', 'yellow')
    color_print('0. Preform pre process operations', 'yellow')
    color_print('1. Install Experiment', 'yellow')
    color_print('2. Update Experiment:', 'yellow')
    color_print('3. Execute Experiment:', 'yellow')
    color_print('4. Update libscapi:', 'yellow')
    selection = input('Your choice:')

    e2e.config_file_path = conf_file_path

    if selection == '0':
        e2e.pre_process()
    elif selection == '1':
        e2e.install_experiment()
    elif selection == '2':
        e2e.update_experiment()
    elif selection == '3':
        e2e.execute_experiment()
    elif selection == '4':
        e2e.update_libscapi()


def print_analysis_menu(conf_file_path):
    color_print('Choose analysis task to be executed:', 'green')
    color_print('1. Download & Analyze Results', 'green')
    color_print('2. Download Results', 'green')
    color_print('3. Analyze Results', 'green')
    color_print('4. Upload data to Elasticsearch', 'green')
    selection = input('Your choice:')

    ar.config_file_path = conf_file_path

    if selection == '1':
        ar.download_data()
        ar.analyze_all()
    elif selection == '2':
        ar.download_data()
    elif selection == '3':
        ar.analyze_all()
    elif selection == '4':
        ue.config_file_path = conf_file_path
        ue.upload_data()


def main():
    selection = print_main_menu()

    while not selection == '4':
        if int(selection) > 4:
            print('Choose valid option!')
            selection = print_main_menu()
            continue

        color_print('Enter configuration file(s):', 'blue')
        conf_file_path = input('Configuration file path (current path is: %s): ' % os.getcwd())

        if selection == '1':
            print_instances_management_menu(conf_file_path)

        elif selection == '2':
            print_execution_menu(conf_file_path)

        elif selection == '3':
            print_analysis_menu(conf_file_path)

        selection = print_main_menu()


if __name__ == '__main__':
    main()
