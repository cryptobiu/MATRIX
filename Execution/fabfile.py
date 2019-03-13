import os
import json
from pathlib import Path
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
def install_git_project(username, password, git_branch, git_address, working_directory, external):
    """
    Install the protocol at the working directory with the GitHub credentials
    :type username str
    :param username: GitHub username
    :type password str
    :param password: GitHub password
    :type git_branch str
    :param git_branch: GitHub project branch
    :type git_address str
    :param git_address: GitHub project address
    :type working_directory str
    :param working_directory: directory to clone the GutHub repository to
    :type external str
    :param external: indicate if libscapi protocol or not
    """
    if not exists(working_directory):
        run(f'git clone {git_address.format(username, password)} {working_directory}')

    external = eval(external)
    with cd(working_directory):
        run('git pull')
        run(f'git checkout {git_branch}')
        if external:
            with cd(f'{working_directory}/MATRIX'):
                run('. ./build.sh')
        else:
            if exists(f'{working_directory}/CMakeLists.txt'):
                sudo('rm -rf CMakeFiles CMakeCache.txt Makefile')
                run('cmake .')
            run('make')
            with warn_only():
                run('7za -y x \"*.7z\"')


@task
def update_libscapi():
    """
    Update libscapi library on the remote servers from dev branch
    """
    with cd('libscapi/'):
        run('git checkout dev')
        run('git pull')
        run('make')


@task
def run_protocol(config_file, args, executable_name, working_directory):
    """
    Execute the protocol on remote servers
    :type config_file str
    :param config_file: configuration file directory
    :type args str
    :param args: the arguments for the protocol, separated by `@`
    :type executable_name str
    :param executable_name: the executable file name
    :type working_directory str
    :param working_directory: the executable file dir
    """
    with open(config_file) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
        external_protocol = json.loads(data['isExternal'].lower())
        if 'aws' in data['CloudProviders']:
            regions = data['CloudProviders']['aws']['regions']
        elif 'azure' in data['CloudProviders']:
            regions = data['CloudProviders']['azure']['regions']
        elif len(data['CloudProviders']) > 1:
            regions = data['CloudProviders']['aws']['regions'] + data['CloudProviders']['azure']['regions']
        elif 'servers' in data['CloudProviders']:
            regions = data['CloudProviders']['servers']['regions']
        else:
            regions = []

        vals = args.split('@')
        values_str = ''

        for val in vals:
            # for external protocols
            if val == 'partyid':
                values_str += f'{str(env.hosts.index(env.host) - 1)} '
            else:
                values_str += f'{val} '

        # local execution
        if len(regions) == 0:
            number_of_parties = len(env.hosts)
            local(f'cp InstancesConfigurations/parties.conf {working_directory}/MATRIX')
            for idx in range(number_of_parties):
                if external_protocol:
                    local(f'cd {working_directory}/MATRIX && ./{executable_name} {idx} {values_str} &')
                else:
                    local(f'cd {working_directory} && ./{executable_name} partyID {idx} {values_str} &')

        else:
            party_id = env.hosts.index(env.host)

            with warn_only():
                sudo("kill -9 `ps aux | grep %s | awk '{print $2}'`" % executable_name)

            if 'inputs0' in values_str:
                values_str = values_str.replace('input_0.txt', f'input_{str(party_id)}.txt')

            with cd(working_directory):
                if not external_protocol:
                    if len(regions) > 1:
                        put(f'InstancesConfigurations/parties{party_id}.conf', run('pwd'))
                        run(f'mv parties{party_id}.conf parties.conf')
                    else:
                        put('InstancesConfigurations/parties.conf', run('pwd'))
                    sudo(f'chmod +x {executable_name}')
                    run(f'./{executable_name} partyID {party_id} {values_str}')
                    with open('Execution/execution_log.log', 'a+') as log_file:
                        log_file.write(f'{values_str}\n')
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
                                    coordinator_values_str += f'{coordinator_val} '

                                with warn_only():
                                    sudo("kill -9 `ps aux | grep %s | awk '{print $2}'`" % executable_name)
                                    # required for SCALE-MAMBA to rsync between AWS instances
                                    put(env.key_filename[0], run('pwd'))

                                run(f'{coordinator_executable} {coordinator_values_str}')
                                with open('Execution/execution_log.log', 'a+') as log_file:
                                    log_file.write(f'{values_str}\n' % values_str)
                            else:
                                if len(regions) > 1:
                                    put(f'InstancesConfigurations/parties{party_id}.conf', run('pwd'))
                                    run(f'mv parties{party_id}.conf parties.conf')

                                run(f'./{executable_name} {party_id - 1} {values_str}')
                                with open('Execution/execution_log.log', 'a+') as log_file:
                                    log_file.write(f'{values_str}\n')
                        else:
                            # run external protocols with no coordinator
                            if len(regions) > 1:
                                put(f'InstancesConfigurations/parties{party_id}.conf', run('pwd'))
                                run(f'mv parties{party_id}.conf parties.conf')
                            else:
                                put('InstancesConfigurations/parties.conf', run('pwd'))
                            run('mkdir -p logs')
                            run(f'./{executable_name} {party_id} {values_str}')
                            with open('Execution/execution_log.log', 'a+') as log_file:
                                log_file.write(f'{values_str}\n')


@task
def run_protocol_profiler(config_file, args, executable_name, working_directory):
    """
    Execute the protocol on remote servers with profiler.
    The first party is executed with profiler, the other executed normally
    :type config_file str
    :param config_file: configuration file directory
    :type args str
    :param args: the arguments for the protocol, separated by `@`
    :type executable_name str
    :param executable_name: the executable file name
    :type working_directory str
    :param working_directory: the executable file dir
    """
    with open(config_file) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
        external_protocol = json.loads(data['isExternal'].lower())
        if 'aws' in data['CloudProviders']:
            regions = data['CloudProviders']['aws']['regions']
        elif 'azure' in data['CloudProviders']:
            regions = data['CloudProviders']['azure']['regions']
        else:
            regions = data['CloudProviders']['aws']['regions'] + data['CloudProviders']['azure']['regions']
        vals = args.split('@')
        values_str = ''

        for val in vals:
            # for external protocols
            if val == 'partyid':
                values_str += f'{str(env.hosts.index(env.host) - 1)} '
            else:
                values_str += f'{val} '

        with cd(working_directory):
            party_id = env.hosts.index(env.host)

            with warn_only():
                sudo("kill -9 `ps aux | grep %s | awk '{print $2}'`" % executable_name)

            if 'inputs0' in values_str:
                values_str = values_str.replace('input_0.txt', f'input_{str(party_id)}.txt')

            if not external_protocol:
                if len(regions) > 1:
                    put(f'InstancesConfigurations/parties{party_id}.conf', run('pwd'))
                    run(f'mv parties{party_id}s.conf parties.conf')
                else:
                    put('InstancesConfigurations/parties.conf', run('pwd'))
                if party_id == 0:
                    run(f'valgrind --tool=callgrind ./{executable_name} partyID {party_id} {values_str}')
                    get('callgrind.out.*', os.getcwd())
                else:
                    run(f'./{executable_name} partyID {party_id} {values_str}')
                    with open('Execution/execution_log.log', 'a+') as log_file:
                        log_file.write(f'{values_str}\n')


@task
def run_protocol_with_latency(config_file, args, executable_name, working_directory):
    """
    Execute the protocol on remote servers with network latency
    :type config_file str
    :param config_file: configuration file directory
    :type args str
    :param args: the arguments for the protocol, separated by `@`
    :type executable_name str
    :param executable_name: the executable file name
    :type working_directory str
    :param working_directory: the executable file dir
    """
    with open(config_file) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
        external_protocol = json.loads(data['isExternal'].lower())
        if 'aws' in data['CloudProviders']:
            regions = data['CloudProviders']['aws']['regions']
        elif 'azure' in data['CloudProviders']:
            regions = data['CloudProviders']['azure']['regions']
        else:
            regions = data['CloudProviders']['aws']['regions'] + data['CloudProviders']['azure']['regions']
        vals = args.split('@')
        values_str = ''

        for val in vals:
            # for external protocols
            if val == 'partyid':
                values_str += f'{str(env.hosts.index(env.host) - 1)} '
            else:
                values_str += f'{val} '

        with cd(working_directory):
            # the warning required for multi executions.
            # If you delete this line it will failed if you don't reboot the servers
            with warn_only():
                sudo('tc qdisc add dev ens5 root netem delay 300ms')

            party_id = env.hosts.index(env.host)

            with warn_only():
                sudo("kill -9 `ps aux | grep %s | awk '{print $2}'`" % executable_name)

            if 'inputs0' in values_str:
                values_str = values_str.replace('input_0.txt', f'input_{str(party_id)}.txt')

            if not external_protocol:
                if len(regions) > 1:
                    put(f'InstancesConfigurations/parties{party_id}.conf', run('pwd'))
                    run(f'mv parties{party_id}.conf parties.conf')
                else:
                    put('InstancesConfigurations/parties.conf', run('pwd'))

                run(f'./{executable_name} partyID {party_id} {values_str}')
                with open('Execution/execution_log.log', 'a+') as log_file:
                    log_file.write(f'{values_str}\n')


@task
def collect_results(results_server_directory, results_local_directory, is_external):
    """
    :type results_server_directory str
    :param results_server_directory: the remote directory of the JSON results files
    :type results_local_directory str
    :param results_local_directory: the directory that the results are copied too
    :type is_external str
    :param is_external: indicate if libscapi protocol or not
    """
    local(f'mkdir -p {results_local_directory}' % results_local_directory)
    is_external = eval(is_external)
    if not is_external:
        get(f'{results_server_directory}/*.json', results_local_directory)
    else:
        get(f'{results_server_directory}/MATRIX/logs/*.log', results_local_directory)


@task
def get_logs(logs_directory):
    """
    Collect logs from the specified working directory
    :type logs_directory str
    :param logs_directory: logs files directory
    """
    local('mkdir -p logs')
    get(f'{logs_directory}/*.log', f'{Path.home()}/MATRIX/logs')
