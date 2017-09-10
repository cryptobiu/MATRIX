import json
import os


def install_experiment(experiment_name, git_branch):
    os.system('fab -f ExpirementExecute/fabfile.py install_git_project:%s,%s' % (experiment_name, git_branch))


with open('config.json') as data_file:
    data = json.load(data_file)
    machine_type = data['AWS Instance Type']
    price_bids = data['AWS Pricing Bidding']
    request_time = data['ExecRequestTime']
    is_published = data['IsPublished']
    network_type = data['Network']
    number_of_parties = data['Number Of Parties']
    number_of_reptions = data['Number of Repetitions']
    protocol = data['Protocol']
    commit_id = data['Git commit id']
    git_branch = data['Git Branch']

install_experiment(protocol, git_branch)
