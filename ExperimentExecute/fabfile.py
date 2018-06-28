import json
import time
from collections import OrderedDict
from fabric.api import *
from fabric.contrib.files import exists
from os.path import expanduser

env.hosts = open('InstancesConfigurations/public_ips', 'r').read().splitlines()
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
def install_git_project(git_branch, working_directory, git_address, external, install_script):
    if external == 'True':
        put('ExternalProtocols/%s' % install_script, run('pwd'))
        sudo('chmod +x %s' % install_script)
        run('./%s' % install_script)

    else:
        if not exists('%s' % working_directory):
            run('git clone %s' % git_address)

    with cd('%s' % working_directory):
        run('git pull')
        run('git checkout %s ' % git_branch)
        if exists('%s/CMakeLists.txt' % working_directory):
            sudo('rm -rf CMakeFiles CMakeCache.txt Makefile')
            run('cmake .')
        run('make')


@task
def update_libscapi(branch):
    with cd('libscapi/'):
        run('git checkout %s' % branch)
        run('git pull')
        run('make')


@task
def run_protocol(config_file, args):
    with open(config_file) as data_file:

        data = json.load(data_file, object_pairs_hook=OrderedDict)
        protocol_name = data['protocol']
        executable_name = data['executableName']
        working_directory = data['workingDirectory']
        external_protocol = data['isExternal']
        regions = list(data['regions'].values())
        vals = args.split('@')
        values_str = ''

        for val in vals:
            # for external protocols
            if val == 'partyid':
                values_str += '%s ' % str(env.hosts.index(env.host) - 1)
            else:
                values_str += '%s ' % val

        with cd(working_directory):
            if exists('*.7z'):
                run('7z e *.7z')

            if not exists('logs'):
                run('mkdir -p logs')
            else:
                run('rm logs/*')
                
            party_id = env.hosts.index(env.host)
            sudo('killall -9 %s; exit 0' % executable_name)

            sudo('ldconfig ~/boost_1_64_0/stage/lib/ ~/libscapi/install/lib/')

            if protocol_name == 'MPCFromSD':
                values_str = values_str.replace('inputs0.txt', 'inputs%s.txt' % str(party_id))

            # with warn_only():
            if external_protocol == 'False':
                if len(regions) > 1:
                    put('InstancesConfigurations/parties%s.conf' % party_id, run('pwd'))
                    run('mv parties%s.conf parties.conf' % party_id)
                else:
                    put('InstancesConfigurations/parties.conf', run('pwd'))
                run('./%s -partyID %s %s' % (executable_name, party_id, values_str))

            else:
                if 'coordinatorConfig' in data and env.hosts.index(env.host) == 0:
                    coordinator_executable = data['coordinatorExecutable']
                    coordinator_args = data['coordinatorConfig'].split('@')
                    coordinator_values_str = ''

                    for coordinator_val in coordinator_args:
                        coordinator_values_str += '%s ' % coordinator_val
                    sudo('killall -9 %s; exit 0' % coordinator_executable)
                    run('./%s %s' % (coordinator_executable, coordinator_values_str))

                else:
                    time.sleep(31)
                    if len(regions) > 1:
                        put('InstancesConfigurations/parties%s.conf' % party_id, run('pwd'))
                        put('InstancesConfigurations/multi_regions/party%s/*' % (party_id - 1), run('pwd'))
                        run('mv parties%s.conf parties.conf' % party_id)
                    else:
                        put('InstancesConfigurations/*arties*', run('pwd'))

                    run('./%s %s' % (executable_name, values_str))


@task
def collect_results(results_server_directory, results_local_directory):
    local('mkdir -p %s' % results_local_directory)
    get('%s/*.json' % results_server_directory, results_local_directory)


@task
def get_logs(working_directory):
    local('mkdir -p logs')
    get('%s/logs/*.log' % working_directory, expanduser('~/MATRIX/logs'))


@task
def update_acp_protocol():
    with cd('ACP'):
        run('git pull https://github.com/cryptobiu/ACP')
        with cd('comm_client'):
            run('cmake .')
            run('make')


@task
def kill_process(process_name):
    sudo('killall -9 %s' % process_name)


@task
def deploy_proxy(number_of_proxies):
    # set hosts to be proxy server
    env.host = ['34.239.19.87']

    # kill all existing proxies
    with warn_only():
        sudo('killall -9 cct_proxy')

    with cd('ACP/cct_proxy'):
        put('NodeApp/public/assets/parties.conf', run('pwd'))
        with open('NodeApp/public/assets/parties.conf') as parties_file:
            number_of_peers = len(parties_file.readlines())
            run('./run_multiple_proxies %s %s' % ((int(number_of_proxies) - 1), number_of_peers))

