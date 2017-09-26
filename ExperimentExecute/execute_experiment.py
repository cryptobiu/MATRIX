import json
import os


def install_experiment(experiment_name, git_branch):
    os.system('fab -f ExperimentExecute/fabfile.py install_git_project:%s,%s --parallel --no-pty'
              % (experiment_name, git_branch))


def execute_experiment():
    os.system('fab -f ExperimentExecute/fabfile.py run_protocol --parallel --no-pty')


with open('config.json') as data_file:
    data = json.load(data_file)
    protocol_name = data['protocol']
    git_branch = data['gitBranch']
    pre_process = data['preProcess']

install_experiment(protocol_name, git_branch)
execute_experiment()
