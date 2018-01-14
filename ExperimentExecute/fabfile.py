import json
import sys
import time
from collections import OrderedDict
from fabric.api import *
from fabric.contrib.files import exists
from os.path import expanduser

env.hosts = open('public_ips', 'r').read().splitlines()
env.user = 'ubuntu'
# env.password=''
env.key_filename = [expanduser('~/Keys/matrix.pem')]


@task
def pre_process(working_directory, task_idx):
    sudo('apt-get install python3 -y')
    with cd(working_directory):
        put(expanduser('ExperimentExecute/pre_process.py'))
        run('python3 pre_process.py %s' % task_idx)


@task
def install_git_project(experiment_name, git_branch, working_directory, git_address, external, install_script):

    if external == 'True':
        put('ExternalProtocols/%s' % install_script, run('pwd'))
        sudo('chmod +x %s' % install_script)
        run('./%s' % install_script)

    else:
        if not exists('%s' % working_directory):
            run('git clone %s' % git_address)

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
        # run('git checkout MeasurmentAPI')

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
        run('make')


@task
def run_protocol(config_file, args):
    with open(config_file) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
        protocol_name = data['protocol']
        executable_name = data['executableName']
        working_directory = data['workingDirectory']
        external_protocol = data['external']
        vals = args.split('@')
        values_str = ''

        for val in vals:
            values_str += '%s ' % val

        with cd(working_directory):
            put('parties.conf', run('pwd'))
            if external_protocol == 'True':
                put('ExternalProtocols/%s' % executable_name, run('pwd'))
                sudo('chmod +x %s' % executable_name)

            sudo('killall -9 %s; exit 0' % executable_name)
            sudo('killall -9 Player-Online.x; exit 0')
            sudo('killall -9 Server.x; exit 0')
            sudo('ldconfig ~/boost_1_64_0/stage/lib/ ~/libscapi/install/lib/')
            party_id = env.hosts.index(env.host)

            if protocol_name == 'GMW':
                values_str = values_str.replace('AesInputs0.txt', 'AesInputs%s.txt' % str(party_id))

            with warn_only():
                if external_protocol == 'True':
                    run('./%s -i %s %s' % (executable_name, party_id, values_str))

                else:
                    if 'coordinatorConfig' in data and env.hosts.index(env.host) == len(env.hosts) - 1:
                        coordinator_executable = data['coordinatorExecutable']
                        coordinator_args = list(data['coordinatorConfig'].values())[0].split('@')
                        coordinator_values_str = ''

                        for coordinator_val in coordinator_args:
                            coordinator_values_str += '%s ' % coordinator_val

                        time.sleep(2)
                        run('./%s %s' % (coordinator_executable, coordinator_values_str))

                    else:
                        run('./%s -partyID %s %s' % (executable_name, party_id, values_str))


@task
def collect_results(results_local_directory, results_remote_directory):

    local('mkdir -p %s' % results_remote_directory)
    print(results_remote_directory)
    print(results_local_directory)
    get('%s/*.json' % results_local_directory, results_remote_directory)
