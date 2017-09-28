import json
import os


def install_experiment(experiment_name, git_branch):
    os.system('fab -f ExperimentExecute/fabfile.py install_git_project:%s,%s --parallel --no-pty'
              % (experiment_name, git_branch))


def execute_experiment(repetitions):
    for i in range(repetitions):
        os.system('fab -f ExperimentExecute/fabfile.py run_protocol --parallel --no-pty')


def collect_results(results_remote_directory, results_local_directory):
    os.system('fab -f ExperimentExecute/fabfile.py collect_results:%s,%s --parallel --no-pty'
              %(results_remote_directory, results_local_directory))


with open('config.json') as data_file:
    data = json.load(data_file)
    protocol_name = data['protocol']
    git_branch = data['gitBranch']
    pre_process = data['preProcess']
    results_directory = data['resultsDirectory']
    number_of_repetitions = data['numOfRepetitions']

install_experiment(protocol_name, git_branch)
execute_experiment(number_of_repetitions)
collect_results(protocol_name, results_directory)
