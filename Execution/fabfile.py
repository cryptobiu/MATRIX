import os
import json
import time
from collections import OrderedDict
from fabric.api import *
from fabric.contrib.files import exists


env.hosts = open('InstancesConfigurations/public_ips', 'r').read().splitlines()
# Set this to the username on the machines running the benchmark (possibly 'ubuntu')
env.user = 'ubuntu'
# env.password=''
# Set this to point to where the AWS key is put by MATRIX (possibly ~/Keys/[KEYNAME])
env.key_filename = ['YOUR-KEY']
# Set this to point to where you put the MATRIX root
path_to_matrix = 'YOU PATH TO MATRIX'


@task
def pre_process(working_directory, task_idx):
    if not exists('%s' % working_directory):
        print('Seems you are trying to install dependencies before you install your experiment. That totally makes sense, but that is not how MATRIX works. You need to install the experiment first. Please go do that now and come back.')
    else:
        sudo('apt-get update')
        sudo('apt-get install python3 -y')
        sudo('apt-get install python3-pip -y')
        run('pip3 install boto3')
        with cd(working_directory):
            put('%s/Execution/pre_process.py' % path_to_matrix, working_directory)
            run('python3 pre_process.py %s' % task_idx)

@task
def install_git_project(git_branch, working_directory, git_address, external):
    if not exists('%s' % working_directory):
        run('git clone %s %s' % (git_address, working_directory))

    external = eval(external)
    with cd('%s' % working_directory):
        run('git pull')
        run('git checkout %s ' % git_branch)
        if external:
            with cd('%s/MATRIX' % working_directory):
                run('. ./build.sh')
        else:
            if exists('%s/CMakeLists.txt' % working_directory):
                sudo('rm -rf CMakeFiles CMakeCache.txt Makefile')
                run('cmake .')
            run('make')
            with warn_only():
                run('7za -y x \"*.7z\"')


@task
def update_libscapi(branch):
    with cd('libscapi/'):
        run('git checkout %s' % branch)
        run('git pull')
        run('make')


@task
def run_protocol(config_file, args, executable_name, working_directory):
    with open(config_file) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
        external_protocol = json.loads(data['isExternal'].lower())
        if 'aws' in data['CloudProviders']:
            regions = data['CloudProviders']['aws']['regions']
        elif 'scaleway' in data['CloudProviders']:
            regions = data['CloudProviders']['scaleway']['regions']
        elif len(data['CloudProviders']) > 1:
            regions = data['CloudProviders']['aws']['regions'] + data['CloudProviders']['scaleway']['regions']
        elif 'servers' in data['CloudProviders']:
            regions = data['CloudProviders']['servers']['servers']['regions']
        else:
            regions = []

        vals = args.split('@')
        values_str = ''

        for val in vals:
            # for external protocols
            if val == 'partyid':
                values_str += '%s ' % str(env.hosts.index(env.host) - 1)
            else:
                values_str += '%s ' % val

        # local execution
        if len(regions) == 0:
            number_of_parties = len(env.hosts)
            local('cp InstancesConfigurations/parties.conf %s/MATRIX' % working_directory)
            for idx in range(number_of_parties):
                if external_protocol:
                    local('cd %s/MATRIX && ./%s %s %s &' % (working_directory, executable_name, idx, values_str))
                else:
                    local('cd %s && ./%s partyID %s %s &' % (working_directory, executable_name, idx, values_str))

        else:
            with cd(working_directory):
                if env.user == 'root':
                    party_id = env.hosts.index('root@%s' % env.host)
                else:
                    party_id = env.hosts.index(env.host)

                with warn_only():
                    sudo("kill -9 `ps aux | grep %s | awk '{print $2}'`" % executable_name)

                if 'inputs0' in values_str:
                    values_str = values_str.replace('input_0.txt', 'input_%s.txt' % str(party_id))

                # # apply delay if needed
                #
                # if 'delay' in data:
                #     sudo('tc qdisc del dev ens5 root netem')
                #     sudo('tc qdisc add dev ens5 root netem delay %sms' % data['delay'])
                #     time.sleep(10)

                if not external_protocol:
                    if len(regions) > 1:
                        put('InstancesConfigurations/parties%s.conf' % party_id, run('pwd'))
                        run('mv parties%s.conf parties.conf' % party_id)
                    else:
                        put('InstancesConfigurations/parties.conf', run('pwd'))
                    run('./%s partyID %s %s' % (executable_name, party_id, values_str))
                    with open('Execution/execution_log.log', 'a+') as log_file:
                        log_file.write('%s\n' % values_str)
                else:
                    # run external protocols
                    with cd('MATRIX'):
                        if 'coordinatorConfig' in data:
                            # run protocols  with coordinator
                            put('InstancesConfigurations/parties.conf', run('pwd'))
                            # public ips are required for SCALE-MAMBA
                            put('InstancesConfigurations/public_ips', run('pwd'))

                            if env.hosts.index(env.host) == 0:
                                coordinator_executable = data['coordinatorExecutable']
                                coordinator_args = data['coordinatorConfig'].split('@')
                                coordinator_values_str = ''

                                for coordinator_val in coordinator_args:
                                    coordinator_values_str += '%s ' % coordinator_val

                                with warn_only():
                                    sudo("kill -9 `ps aux | grep %s | awk '{print $2}'`" % coordinator_executable)
                                    # required for SCALE-MAMBA to rsync between AWS instances
                                    put(env.key_filename[0], run('pwd'))
                                run('./%s %s' % (coordinator_executable, coordinator_values_str))
                                with open('Execution/execution_log.log', 'a+') as log_file:
                                    log_file.write('%s\n' % values_str)
                            else:
                                if len(regions) > 1:
                                    put('InstancesConfigurations/parties%s.conf' % party_id, run('pwd'))
                                    run('mv parties%s.conf parties.conf' % party_id)

                                run('. ./%s %s %s' % (executable_name, party_id - 1, values_str))
                                with open('Execution/execution_log.log', 'a+') as log_file:
                                    log_file.write('%s\n' % values_str)
                        else:
                            # run external protocols with no coordinator
                            if len(regions) > 1:
                                put('InstancesConfigurations/parties%s.conf' % party_id, run('pwd'))
                                run('mv parties%s.conf parties.conf' % party_id)
                            else:
                                put('InstancesConfigurations/parties.conf', run('pwd'))
                            run('mkdir -p logs')
                            run('. ./%s %s %s' % (executable_name, party_id, values_str))
                            with open('Execution/execution_log.log', 'a+') as log_file:
                                log_file.write('%s\n' % values_str)

@task
def run_protocol_profiler(config_file, args, executable_name, working_directory):
    with open(config_file) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
        external_protocol = json.loads(data['isExternal'].lower())
        if 'aws' in data['CloudProviders']:
            regions = data['CloudProviders']['aws']['regions']
        elif 'scaleway' in data['CloudProviders']:
            regions = data['CloudProviders']['scaleway']['regions']
        else:
            regions = data['CloudProviders']['aws']['regions'] + data['CloudProviders']['scaleway']['regions']
        vals = args.split('@')
        values_str = ''

        for val in vals:
            # for external protocols
            if val == 'partyid':
                values_str += '%s ' % str(env.hosts.index(env.host) - 1)
            else:
                values_str += '%s ' % val

        with cd(working_directory):
            if env.user == 'root':
                party_id = env.hosts.index('root@%s' % env.host)
            else:
                party_id = env.hosts.index(env.host)

            with warn_only():
                sudo("kill -9 `ps aux | grep %s | awk '{print $2}'`" % executable_name)

            if 'inputs0' in values_str:
                values_str = values_str.replace('input_0.txt', 'input_%s.txt' % str(party_id))

            if not external_protocol:
                if len(regions) > 1:
                    put('InstancesConfigurations/parties%s.conf' % party_id, run('pwd'))
                    run('mv parties%s.conf parties.conf' % party_id)
                else:
                    put('InstancesConfigurations/parties.conf', run('pwd'))
                if party_id == 0:
                    run('valgrind --tool=callgrind ./%s partyID %s %s'
                        % (executable_name, party_id, values_str))
                    get('callgrind.out.*', os.getcwd())
                else:
                    run('./%s partyID %s %s' % (executable_name, party_id, values_str))
                    with open('Execution/execution_log.log', 'a+') as log_file:
                        log_file.write('%s\n' % values_str)


@task
def run_protocol_with_latency(config_file, args, executable_name, working_directory):
    with open(config_file) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
        external_protocol = json.loads(data['isExternal'].lower())
        if 'aws' in data['CloudProviders']:
            regions = data['CloudProviders']['aws']['regions']
        elif 'scaleway' in data['CloudProviders']:
            regions = data['CloudProviders']['scaleway']['regions']
        else:
            regions = data['CloudProviders']['aws']['regions'] + data['CloudProviders']['scaleway']['regions']
        vals = args.split('@')
        values_str = ''

        for val in vals:
            # for external protocols
            if val == 'partyid':
                values_str += '%s ' % str(env.hosts.index(env.host) - 1)
            else:
                values_str += '%s ' % val

        with cd(working_directory):
            # the warning required for multi executions.
            # If you delete this line it will failed if you don't reboot the servers
            with warn_only():
                sudo('tc qdisc add dev ens5 root netem delay 300ms')
            if env.user == 'root':
                party_id = env.hosts.index('root@%s' % env.host)
            else:
                party_id = env.hosts.index(env.host)

            with warn_only():
                sudo("kill -9 `ps aux | grep %s | awk '{print $2}'`" % executable_name)

            if 'inputs0' in values_str:
                values_str = values_str.replace('input_0.txt', 'input_%s.txt' % str(party_id))

            if not external_protocol:
                if len(regions) > 1:
                    put('InstancesConfigurations/parties%s.conf' % party_id, run('pwd'))
                    run('mv parties%s.conf parties.conf' % party_id)
                else:
                    put('InstancesConfigurations/parties.conf', run('pwd'))
                if party_id == 0:
                    run('valgrind --tool=callgrind ./%s partyID %s %s'
                        % (executable_name, party_id, values_str))
                    get('callgrind.out.*', os.getcwd())
                else:
                    run('./%s partyID %s %s' % (executable_name, party_id, values_str))
                    with open('Execution/execution_log.log', 'a+') as log_file:
                        log_file.write('%s\n' % values_str)


@task
def collect_results(results_server_directory, results_local_directory, is_external):
    local('mkdir -p %s' % results_local_directory)
    is_external = eval(is_external)
    if not is_external:
        get('%s/*.json' % results_server_directory, results_local_directory)
    else:
        get('%s/MATRIX/logs/*.log' % results_server_directory, results_local_directory)


@task
def update_acp_protocol():
    with cd('ACP'):
        run('git pull https://github.com/cryptobiu/ACP')
        with cd('comm_client'):
            run('cmake .')
            run('make')


@task
def deploy_proxy(number_of_proxies):
    # set hosts to be proxy server
    env.host = ['34.239.19.87']

    # kill all existing proxies
    with warn_only():
        sudo("kill -9 `ps aux | grep cct_proxy | awk '{print $2}'`")

    with cd('ACP/cct_proxy'):
        put('NodeApp/public/assets/parties.conf', run('pwd'))
        with open('NodeApp/public/assets/parties.conf') as parties_file:
            number_of_peers = len(parties_file.readlines())
            run('./run_multiple_proxies %s %s' % ((int(number_of_proxies) - 1), number_of_peers))

