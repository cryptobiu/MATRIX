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
def pre_process(experiment_name):
    with cd('/home/ubuntu/%s' % experiment_name):
        put(expanduser('ExperimentExecute/pre_process.py'))
        run('python 3 pre_process.py')


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
def update_git_project(working_directory):

    with cd('%s' % working_directory):
        run('git pull')

        if exists('%s/CMakeLists.txt' % working_directory):
            with settings(warn_only=True):
                run('make clean')
                sudo('rm -rf CMakeFiles CMakeCache.txt Makefile')
            run('cmake .')
        run('make')


@task
def update_libscapi():
    with cd('libscapi/'):
        run('git pull')

        with settings(warn_only=True):
            sudo('rm -rf CMakeFiles CMakeCache.txt Makefile')
        run('cmake .')
        sudo('make')


@task
def run_protocol(config_file, args):
    with open(config_file) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
        protocol_name = data['protocol']
        executable_name = data['executableName']
        working_directory = data['workingDirectory']

        vals = args.split('@')
        values_str = ''

        for val in vals:
            values_str += '%s ' % val

        print(values_str)
        with cd(working_directory):
            put('parties.conf', run('pwd'))
            sudo('killall -9 %s; exit 0' % executable_name)
            sudo('ldconfig ~/boost_1_64_0/stage/lib/ ~/libscapi/install/lib/')
            party_id = env.hosts.index(env.host)

            if protocol_name == 'GMW':
                values_str = values_str.replace('AesInputs0.txt', 'AesInputs%s.txt' % str(party_id))

            with warn_only():
                run('./%s -partyID %s %s' % (executable_name, party_id, values_str))

    sys.stdout.flush()


@task
def collect_results(results_local_directory, results_remote_directory):

    local('mkdir -p %s' % results_remote_directory)
    get('%s/*.json' % results_local_directory, results_remote_directory)
