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
task_idx = sys.argv[2]


def pre_process(working_directory, pre_process_task):
    print('Performing pre process operations')
    os.system('fab -f ExperimentExecute/fabfile.py pre_process:%s,%s --parallel --no-pty'
              % (working_directory, pre_process_task))


def install_experiment(experiment_name, git_branch, working_directory,
                       git_address, external_protocol=False, install_script=''):
    print('Installing experiment %s...' % experiment_name)
    os.system('fab -f ExperimentExecute/fabfile.py install_git_project:%s,%s,%s,%s,%s,%s --parallel --no-pty'
              % (experiment_name, git_branch, working_directory, git_address, external_protocol, install_script))


def update_experiment(experiment_name, working_directory):
    print('Updating experiment %s...' % experiment_name)
    os.system('fab -f ExperimentExecute/fabfile.py update_git_project:%s --parallel --no-pty' % working_directory)


def execute_experiment(repetitions, experiment_name, configurations, working_directory):

    # before executing experiment delete all the existing log files
    os.system('fab -f ExperimentExecute/fabfile.py delete_json_files:%s' % working_directory)

    for i in range(repetitions):
        print('Executing experiment %s...' % experiment_name)
        for idx in range(len(configurations)):
            os.system('fab -f ExperimentExecute/fabfile.py run_protocol:%s,%s --parallel --no-pty'
                      % (config_file_path, configurations[idx]))


def update_libscapi():
    print('Updating libscapi library')
    branch = input('Enter libscapi branch to update from:')
    os.system('fab -f ExperimentExecute/fabfile.py update_libscapi:%s --parallel --no-pty' % branch)


with open(config_file_path) as data_file:
    data = json.load(data_file, object_pairs_hook=OrderedDict)
    protocol_name = data['protocol']
    git_address = ''
    git_branch = ''
    pre_process_task = ''
    external_protocol = ''
    install_script = ''

    if 'gitAddress' in data:
        git_address = data['gitAddress']
        git_branch = data['gitBranch']
    # pre_process_state = data['preProcess']
    now = datetime.datetime.now()
    number_of_repetitions = data['numOfRepetitions']
    working_directory = data['workingDirectory']
    configurations = list(data['configurations'].values())
    if 'preProcessTask' in data.keys():
        pre_process_task = data['preProcessTask']
    if data['external'] == 'True':
        external_protocol = data['external']
        install_script = data['installScript']

if task_idx == '0':
    pre_process(working_directory, pre_process_task)

elif task_idx == '1':
    install_experiment(protocol_name, git_branch, working_directory, git_address, external_protocol, install_script)

elif task_idx == '2':
    update_experiment(protocol_name, working_directory)

elif task_idx == '3':
    execute_experiment(number_of_repetitions, protocol_name, configurations, working_directory)

elif task_idx == '4':
    update_libscapi()

else:
    print('task not recognize. these tasks are allowed:\n'
          '0. Pre-process\n'
          '1. Install\n'
          '2. Update\n'
          '3. Execute\n'
          '4. Update libscapi\n')

