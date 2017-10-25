import json
import sys
from collections import OrderedDict

from fabric.api import *
from fabric.contrib.files import exists
from os.path import expanduser

env.hosts = open('public_ips', 'r').read().splitlines()
env.user = 'ubuntu'
env.key_filename = [expanduser('~/Keys/matrix.pem')]


@task
def pre_process():
    put('ExperimentExecute/pre_process.py', '~')
    run('python3 pre_process.py')

# @task
# def pre_process(experiment_name):
#     with cd('/home/ubuntu/%s' % experiment_name):
#         if exists('pre_process.py'):
#             run('python 3 pre_process.py')


@task
def install_git_project(experiment_name, git_branch, working_directory):

    if not exists('%s' % working_directory):
        run('git clone https://liorbiu:4aRotdy0vOhfvVgaUaSk@github.com/cryptobiu/%s.git' % experiment_name)

    if experiment_name == 'LowCostConstantRoundMPC':
        put(expanduser('~/Desktop/libOTe.tar.gz'))
        run('tar -xf libOTe.tar.gz')
        with cd('libOTe'):

            run('rm -rf CMakeFiles CMakeCache.txt Makefile')
            run('cmake .')
            run('make')

    with cd('%s' % working_directory):
        run('git checkout %s ' % git_branch)
        if exists('%s/CMakeLists.txt' % working_directory):
            sudo('rm -rf CMakeFiles CMakeCache.txt Makefile')
            run('cmake .')
        run('make')


@task
def update_git_project(experiment_name, git_branch, working_directory):

    with cd('%s' % working_directory):
        run('git pull')
        run('make clean')
        if exists('%s/CMakeLists.txt' % working_directory):
            sudo('rm -rf CMakeFiles CMakeCache.txt Makefile')
            run('cmake .')
        run('make')


@task
def update_libscapi():
    with cd('libscapi/'):
        run('git pull')
        run('cmake .')
        sudo('make')


@task
def run_protocol(config_file):
    with open(config_file) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
        protocol_name = data['protocol']
        executable_name = data['executableName']
        configurations = list(data['configurations'].values())
        working_directory = data['workingDirectory']

        # list of all configurations after parse
        lconf = list()

        for i in range(len(configurations)):
            print(configurations[i])
            vals = configurations[i]
            values_str = ''

            for val in vals:
                values_str += val

            lconf.append(values_str)

        with cd(working_directory):
            put('parties.conf', run('pwd'))
            sudo('killall -9 %s; exit 0' % executable_name)
            sudo('ldconfig ~/boost_1_64_0/stage/lib/ ~/libscapi/install/lib/')
            party_id = env.hosts.index(env.host)

            for idx in range(len(lconf)):
                if protocol_name == 'GMW':
                    lconf[idx] = lconf[idx].replace('AesInputs0.txt', 'AesInputs%s.txt' % str(party_id))
                print(lconf[idx])
                run('./%s -partyID %s %s' % (executable_name, party_id, lconf[0]))

    sys.stdout.flush()


@task
def collect_results(results_local_directory, results_remote_directory):

    local('mkdir -p %s' % results_remote_directory)
    get('%s/*.json' % results_local_directory, results_remote_directory)
