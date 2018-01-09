import json
import os
import sys

import datetime
from collections import OrderedDict

if len(sys.argv) != 3:
    print(sys.argv)
    print('Wrong number of arguments supplied\n Exiting...')
    exit(-1)
config_file_path = sys.argv[1]
task_name = sys.argv[2]


def pre_process(working_directory, pre_process_task):
    print('Performing pre process operations')
    os.system('fab -f ExperimentExecute/fabfile.py pre_process:%s,%s --parallel --no-pty'
              % (working_directory, pre_process_task))


def update_libscapi():
    print('Updating libscapi library')
    os.system('fab -f ExperimentExecute/fabfile.py update_libscapi --parallel --no-pty')


def install_experiment(experiment_name, git_branch, working_directory, git_address):
    print('Installing experiment %s...' % experiment_name)
    os.system('fab -f ExperimentExecute/fabfile.py install_git_project:%s,%s,%s,%s --parallel --no-pty'
              % (experiment_name, git_branch, working_directory, git_address))


def update_experiment(experiment_name, working_directory):
    print('Updating experiment %s...' % experiment_name)
    os.system('fab -f ExperimentExecute/fabfile.py update_git_project:%s --parallel --no-pty' % working_directory)


def execute_experiment(repetitions, experiment_name, configurations):
    for i in range(repetitions):
        print('Executing experiment %s...' % experiment_name)
        for idx in range(len(configurations)):
            os.system('fab -f ExperimentExecute/fabfile.py run_protocol:%s,%s --parallel --no-pty'
                      % (config_file_path, configurations[idx]))


def collect_results(results_remote_directory, results_local_directory, experiment_name):
    print('Collecting results for experiment %s...' % experiment_name)
    os.system('fab -f ExperimentExecute/fabfile.py collect_results:%s,%s --parallel --no-pty'
              % (results_remote_directory, results_local_directory))


def analyze_results(experiment_name, config_file_path, results_path):
    print('analyze results for experiment %s...' % experiment_name)
    os.system('python3 ExperimentReport/analyze_results.py %s %s' % (config_file_path, results_path))


with open(config_file_path) as data_file:
    data = json.load(data_file, object_pairs_hook=OrderedDict)
    protocol_name = data['protocol']
    git_address = data['gitAddress']
    git_branch = data['gitBranch']
    # pre_process_state = data['preProcess']
    now = datetime.datetime.now()
    results_directory = data['resultsDirectory'] + '_' + str(now.year) + str(now.month) + str(now.day) + \
                        str(now.hour) + str(now.minute)
    number_of_repetitions = data['numOfRepetitions']
    working_directory = data['workingDirectory']
    configurations = list(data['configurations'].values())
    if 'preProcessTask' in data.keys():
        pre_process_task = data['preProcessTask']

if task_name == 'Pre-process':
    pre_process(working_directory, pre_process_task)
elif task_name == 'Install':
    install_experiment(protocol_name, git_branch, working_directory, git_address)
elif task_name == 'Update':
    update_experiment(protocol_name, working_directory)
elif task_name == 'Execute':
    execute_experiment(number_of_repetitions, protocol_name, configurations)
elif task_name == 'Results':
    collect_results(os.path.join('', working_directory), os.path.join('', results_directory), protocol_name)
    analyze_results(protocol_name, config_file_path, results_directory)
elif task_name == 'Analyze':
    results_directory = input('Enter results directory current path is: %s): ' % os.getcwd())
    analyze_results(protocol_name, config_file_path, results_directory)
else:
    print('task not recognize. these tasks are allowed:\n'
          '1. Pre-process\n'
          '2. Install\n'
          '3. Update\n'
          '4. Execute\n'
          '5. Results\n'
          '6. Analyze\n')

