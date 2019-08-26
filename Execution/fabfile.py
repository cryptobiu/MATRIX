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
env.key_filename = [f'{Path.home()}/Keys/Matrixuseast1.pem']
# Set this to point to where you put the MATRIX root
path_to_matrix = 'YOU PATH TO MATRIX'


@task
def install_git_project(username, password, git_branch, git_address, working_directory):
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
    :param working_directory: directory to clone the GitHub repository to
    """
    if not exists(working_directory):
        run(f'git clone {git_address.format(username, password)} {working_directory}')

    with cd(working_directory):
        run('git pull')
        run(f'git checkout {git_branch}')
        with cd(f'{working_directory}'):
            run('./MATRIX/build.sh')


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
def run_protocol(number_of_regions, args, executable_name, working_directory, external_protocol,
                 coordinator_executable=None, coordinator_config=None):
    """
    Execute the protocol on remote servers
    :type number_of_regions int
    :param number_of_regions: number of regions
    :type args str
    :param args: the arguments for the protocol, separated by `@`
    :type executable_name str
    :param executable_name: the executable file name
    :type working_directory str
    :param working_directory: the executable file dir
    :type external_protocol str
    :param working_directory: the executable file dir
    :type coordinator_executable str
    :param coordinator_executable: coordinator executable name
    :type coordinator_config str
    :param coordinator_config: coordinator args
    """

    vals = args.split('@')
    values_str = ''

    for val in vals:
        # for external protocols
        if val == 'partyid':
            values_str += f'{str(env.hosts.index(env.host) - 1)} '
        else:
            values_str += f'{val} '

    # local execution
    if number_of_regions == 0:
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
            # run external protocols
            with cd('MATRIX'):
                if coordinator_executable is not None:
                    # run protocols  with coordinator
                    put('InstancesConfigurations/parties.conf', working_directory)
                    # public ips are required for SCALE-MAMBA
                    put('InstancesConfigurations/public_ips', working_directory)

                    if env.hosts.index(env.host) == 0:
                        coordinator_args = coordinator_config['coordinatorConfig'].split('@')
                        coordinator_values_str = ''

                        for coordinator_val in coordinator_args:
                            coordinator_values_str += f'{coordinator_val} '

                        with warn_only():
                            sudo("kill -9 `ps aux | grep %s | awk '{print $2}'`" % executable_name)
                            # required for SCALE-MAMBA to rsync between AWS instances
                            put(env.key_filename[0], run('pwd'))

                        run(f'{coordinator_executable} {coordinator_values_str}')
                        try:
                            with open('Execution/execution_log.log', 'a+') as log_file:
                                log_file.write(f'{values_str}\n' % values_str)
                        except EnvironmentError:
                            print('Cannot write data to execution log file')
                    else:
                        if number_of_regions > 1:
                            put(f'InstancesConfigurations/parties{party_id}.conf', working_directory)
                            run(f'mv {working_directory}/parties{party_id}.conf {working_directory}/parties.conf')

                        run(f'./{executable_name} {party_id - 1} {values_str}')
                        try:
                            with open('Execution/execution_log.log', 'a+') as log_file:
                                log_file.write(f'{values_str}\n')
                        except EnvironmentError:
                            print('Cannot write data to execution log file')
                else:
                    # run external protocols with no coordinator
                    if int(number_of_regions) > 1:
                        put(f'InstancesConfigurations/parties{party_id}.conf', working_directory)
                        run(f'mv {working_directory}/parties{party_id}.conf {working_directory}/parties.conf')
                    else:
                        put('InstancesConfigurations/parties.conf', working_directory)
                    run('mkdir -p logs')
                    run(f'./{executable_name} {party_id} {values_str}')
                    try:
                        with open('Execution/execution_log.log', 'a+') as log_file:
                            log_file.write(f'{values_str}\n')
                    except EnvironmentError:
                        print('Cannot write data to execution log file')


@task
def run_protocol_profiler(number_of_regions, args, executable_name, working_directory):
    """
    Execute the protocol on remote servers with profiler.
    The first party is executed with profiler, the other executed normally
    :type number_of_regions int
    :param number_of_regions: number of regions
    :type args str
    :param args: the arguments for the protocol, separated by `@`
    :type executable_name str
    :param executable_name: the executable file name
    :type working_directory str
    :param working_directory: the executable file dir
    """

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
            if number_of_regions > 1:
                put(f'InstancesConfigurations/parties{party_id}.conf', run('pwd'))
                run(f'mv parties{party_id}s.conf parties.conf')
            else:
                put('InstancesConfigurations/parties.conf', run('pwd'))
            if party_id == 0:
                run(f'valgrind --tool=callgrind ./{executable_name} partyID {party_id} {values_str}')
                get('callgrind.out.*', os.getcwd())
            else:
                run(f'./{executable_name} partyID {party_id} {values_str}')
                try:
                    with open('Execution/execution_log.log', 'a+') as log_file:
                        log_file.write(f'{values_str}\n')
                except EnvironmentError:
                    print('Cannot write data to execution log file')


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
            try:
                with open('Execution/execution_log.log', 'a+') as log_file:
                    log_file.write(f'{values_str}\n')
            except EnvironmentError:
                print('Cannot write data to execution log file')


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
    local(f'mkdir -p {results_local_directory}')
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


@task
def delete_old_experiment(working_directory):
    run(f'rm {working_directory}/*.json')
    run(f'rm {working_directory}/*.log')
