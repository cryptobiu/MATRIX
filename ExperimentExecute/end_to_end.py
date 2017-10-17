import json
import os
import sys


config_file_path = sys.argv[1]


def install_experiment(experiment_name, git_branch, working_directory):
    os.system('fab -f ExperimentExecute/fabfile.py install_git_project:%s,%s,%s --parallel --no-pty'
              % (experiment_name, git_branch, working_directory))


def update_experiment(experiment_name, git_branch, working_directory):
    os.system('fab -f ExperimentExecute/fabfile.py update_git_project:%s,%s,%s --parallel --no-pty'
              % (experiment_name, git_branch, working_directory))


def execute_experiment(repetitions):
    for i in range(repetitions):
        os.system('fab -f ExperimentExecute/fabfile.py run_protocol:%s --parallel --no-pty' % config_file_path)


def collect_results(results_remote_directory, results_local_directory):
    os.system('fab -f ExperimentExecute/fabfile.py collect_results:%s,%s --parallel --no-pty'
              %(results_remote_directory, results_local_directory))


with open(config_file_path) as data_file:
    data = json.load(data_file)
    protocol_name = data['protocol']
    git_branch = data['gitBranch']
    pre_process = data['preProcess']
    results_directory = data['resultsDirectory']
    number_of_repetitions = data['numOfRepetitions']
    working_directory = data['workingDirectory']

# install_experiment(protocol_name, git_branch, working_directory)
# update_experiment(protocol_name, git_branch, working_directory)
execute_experiment(number_of_repetitions)
collect_results(working_directory, results_directory)
