import json
import os


def install_experiment(experiment_name, git_branch):
    os.system('fab -f ExperimentExecute/fabfile.py install_git_project:%s,%s --parallel --no-pty'
              % (experiment_name, git_branch))


with open('config.json') as data_file:
    data = json.load(data_file)
    protocol_name = data['Protocol']
    git_branch = data['Git Branch']

install_experiment(protocol_name, git_branch)
