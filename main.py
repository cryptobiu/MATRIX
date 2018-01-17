import os
import colorama

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


def print_instances_management_menu():
    color_print('Choose deployment task', 'red')
    color_print('1. Deploy Instance(s)', 'red')
    color_print('2. Create Key pair(s)', 'red')
    color_print('3. Create security group(s)', 'red')
    color_print('4. Get instances network data', 'red')
    color_print('5. Terminate Machines', 'red')
    selection = input('Your choice:')
    return selection


def print_execution_menu():
    color_print('Choose task to be executed:', 'yellow')
    color_print('0. Preform pre process operations', 'yellow')
    color_print('1. Install Experiment', 'yellow')
    color_print('2. Update Experiment:', 'yellow')
    color_print('3. Execute Experiment:', 'yellow')
    color_print('4. Update libscapi:', 'yellow')
    selection = input('Your choice:')
    return selection


def print_analysis_menu():
    color_print('Choose analysis task to be executed:', 'green')
    color_print('1. Collect & Analyze Results', 'green')
    color_print('2. Analyze Results', 'green')
    selection = input('Your choice:')
    return selection


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
            deploy_selection = print_instances_management_menu()
            if deploy_selection == '5':
                os.system('python3 InstancesManagement/terminate_instances.py %s' % conf_file_path)
            else:
                os.system('python3 InstancesManagement/deploy_instances.py %s %s' % (conf_file_path, deploy_selection))
        elif selection == '2':
            execute_selection = print_execution_menu()
            try:
                os.system('python3 ExperimentExecute/end_to_end.py %s %s' % (conf_file_path, execute_selection))
            except ValueError as ve:
                print(ve)
        elif selection == '3':
            analysis_selection = print_analysis_menu()
            os.system('python3 ExperimentReport/analyze_results.py %s %s' % (conf_file_path, analysis_selection))

        selection = print_main_menu()


if __name__ == '__main__':
    main()
