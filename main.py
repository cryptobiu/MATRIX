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
    color_print('2. Preform pre process operations', 'blue')
    color_print('3. Execute Menu', 'blue')
    color_print('4. Collect & Analyze Results', 'blue')
    color_print('5. Analyze Results', 'blue')
    color_print('6. Terminate Machines', 'blue')
    color_print('7. Exit', 'blue')
    selection = input('Your choice:')
    return selection


def print_deployment_menu():
    color_print('Choose deployment task', 'red')
    color_print('1. Deploy Instance(s)', 'red')
    color_print('2. Create Key pair(s)', 'red')
    color_print('3. Create security group(s)', 'red')
    selection = input('Your choice:')
    return selection


def print_execution_menu():
    color_print('Choose task to be executed:', 'yellow')
    color_print('1. Install Experiment', 'yellow')
    color_print('2. Update Experiment:', 'yellow')
    color_print('3. Execute Experiment:', 'yellow')
    selection = input('Your choice:')
    return selection


def main():
    selection = print_main_menu()

    while not selection == '7':
        if int(selection) > 7:
            print('Choose valid option!')
            selection = print_main_menu()
            continue

        color_print('Enter configuration file(s):', 'blue')
        conf_file_path = input('Configuration file path (current path is: %s): ' % os.getcwd())

        if selection == '1':
            deploy_selection = print_deployment_menu()
            os.system('python3 ImagesDeployment/deploy_machines.py %s %s' % (conf_file_path, deploy_selection))
        elif selection == '2':
            try:
                os.system('python3 ExperimentExecute/end_to_end.py %s Pre-process' % conf_file_path)
            except ValueError as ve:
                print(ve)
        elif selection == '3':
            execute_selection = print_execution_menu()
            if execute_selection == '1':
                    os.system('python3 ExperimentExecute/end_to_end.py %s Install' % conf_file_path)
            elif execute_selection == '2':
                    os.system('python3 ExperimentExecute/end_to_end.py %s Update' % conf_file_path)
            elif execute_selection == '3':
                    os.system('python3 ExperimentExecute/end_to_end.py %s Execute' % conf_file_path)
        elif selection == '4':
                os.system('python3 ExperimentExecute/end_to_end.py %s Results' % conf_file_path)
        elif selection == '5':
                os.system('python3 ExperimentExecute/end_to_end.py %s Analyze' % conf_file_path)
        elif selection == '6':
                os.system('python3 ExperimentExecute/terminate_machines.py %s' % conf_file_path)

        selection = print_main_menu()


if __name__ == '__main__':
    main()
