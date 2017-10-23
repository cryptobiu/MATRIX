import json
import os
import sys

import datetime

config_file_path = sys.argv[1]


def pre_process():
    print('Performing pre process operations')
    os.system('fab -f ExperimentExecute/fabfile.py pre_process --parallel --no-pty')


def update_libscapi():
    print('Updating libscapi library')
    os.system('fab -f ExperimentExecute/fabfile.py update_libscapi --parallel --no-pty')


def install_experiment(experiment_name, git_branch, working_directory):
    print('Installing experiment %s...' % experiment_name)
    os.system('fab -f ExperimentExecute/fabfile.py install_git_project:%s,%s,%s --parallel --no-pty'
              % (experiment_name, git_branch, working_directory))


def update_experiment(experiment_name, git_branch, working_directory):
    print('Updating experiment %s...' % experiment_name)
    os.system('fab -f ExperimentExecute/fabfile.py update_git_project:%s,%s,%s --parallel --no-pty'
              % (experiment_name, git_branch, working_directory))


def execute_experiment(repetitions, experiment_name):
    for i in range(repetitions):
        print('Executing experiment %s...' % experiment_name)
        os.system('fab -f ExperimentExecute/fabfile.py run_protocol:%s --parallel --no-pty' % config_file_path)


def collect_results(results_remote_directory, results_local_directory, experiment_name):
    print('Collecting results for experiment %s...' % experiment_name)
    os.system('fab -f ExperimentExecute/fabfile.py collect_results:%s,%s --parallel --no-pty'
              % (results_remote_directory, results_local_directory))


def analyze_results(experiment_name, config_file_path, results_path):
    print('analyze results for experiment %s...' % experiment_name)
    os.system('python3 ExperimentReport/analyze_results.py %s %s' % (config_file_path, results_path))


with open(config_file_path) as data_file:
    data = json.load(data_file)
    protocol_name = data['protocol']
    git_branch = data['gitBranch']
    pre_process_state = data['preProcess']
    now = datetime.datetime.now()
    results_directory = data['resultsDirectory'] + '_' + str(now.year) + str(now.month) + str(now.day) + \
                        str(now.hour) + str(now.minute)
    number_of_repetitions = data['numOfRepetitions']
    working_directory = data['workingDirectory']

print('Starting running %s protocol with the following configuration:' % protocol_name)
print('Using git branch : %s' % git_branch)
print('Results will be copied to this path: %s' % results_directory)
print(pre_process_state)

sys.stdout.flush()

if pre_process_state == 'True':
    pre_process()


install_experiment(protocol_name, git_branch, working_directory)
execute_experiment(number_of_repetitions, protocol_name)
collect_results(os.path.join('', working_directory), os.path.join('', results_directory), protocol_name)
analyze_results(protocol_name, config_file_path, results_directory)
