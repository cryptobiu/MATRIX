import os
import json
from collections import OrderedDict
from pathlib import Path, PosixPath
from fabric import Connection, SerialGroup as Serial, task


class FabricTasks:

    def __init__(self):

        host_list = open('InstancesConfigurations/public_ips', 'r').read().splitlines()
        self.connections = []
        self.pool = Serial()
        party_id = 0
        for host in host_list:
            c = Connection(host, user='ubuntu', connect_kwargs={
                'key_filename': ['%s/Keys/matrix.pem' % Path.home()]
            })
            c.party_id = party_id
            party_id += 1
            self.connections.append(c)
            self.pool.append(c)

    def pre_process(self, task_idx):
        """
        Execute pre process tasks on the remote hosts.
        :param task_idx: int
        :return: 0 on success, 1 on failure
        """
        for conn in self.pool:
            conn.put('Execution/pre_process.py', Path.home())
        try:
            self.pool.run('python3 pre_process.py %s' % task_idx)
        except BaseException as e:
            print(e.message)
            return 1
        return 0

    def install_git_project(self, username, password, git_branch, working_directory, git_address, external):
        """

        :param username: string
        :param password: string
        :param git_branch: string
        :param working_directory: list[string]
        :param git_address: list[string]
        :param external: string
        :return:
        """

        # result = self.pool.run('ls' % working_directory, warn=True).failed
        # if result:
        self.pool.run('rm -rf %s' % working_directory)
        r = self.pool.run('git clone %s %s' % (git_address.format(username, password), working_directory))

        self.pool.run('cd %s && git pull' % working_directory)
        self.pool.run('cd %s && git checkout %s ' % (working_directory, git_branch))
        if external:
            self.pool.run('cd %s/MATRIX && ./build.sh')
        else:
            if self.pool.run('cd %s && ls CMakeLists.txt' % working_directory, warn=True).succeeded:
                self.pool.run('cd %s && rm -rf CMakeFiles CMakeCache.txt Makefile' % working_directory)
            self.pool.run('cd %s && cmake .' % working_directory)
            self.pool.run('cd %s && make' % working_directory)
            self.pool.run('cd %s && 7za -y x \"*.7z\"' % working_directory, warn=True)

    def run_protocol(self, cxn, config_file, args, executable_name, working_directory, party_id):
        with open(config_file, 'r') as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)
            external_protocol = json.loads(data['isExternal'].lower())
            protocol_name = data['protocol']
            if 'aws' in data['CloudProviders']:
                regions = data['CloudProviders']['aws']['regions']
            elif 'azure' in data['CloudProviders']:
                regions = data['CloudProviders']['azure']['regions']
            elif len(data['CloudProviders']) > 1:
                regions = data['CloudProviders']['aws']['regions'] + data['CloudProviders']['scaleway']['regions']
            else:
                regions = []

        args = ' '.join(args)

        # local execution
        if len(regions) == 0:
            number_of_parties = len(self.pool)
            for idx in range(number_of_parties):
                if external_protocol:
                    cxn.run('cd %s && ./%s %s %s &' % (working_directory, executable_name, idx, args))
                else:
                    cxn.run('cd %s && ./%s partyID %s %s &' % (working_directory, executable_name, idx, args))
        # remote execution
        else:
            # copy parties file to hosts
            if len(regions) > 1:
                cxn.put('InstancesConfigurations/parties%s.conf' % party_id, working_directory)
                cxn.run('mv parties%s.conf parties.conf' % party_id)
            else:
                cxn.put('/home/liork/MATRIX/InstancesConfigurations/parties.conf')
                cxn.run('mv parties.conf HyperMPC')

        cxn.run("kill -9 `ps aux | grep %s | awk '{print $2}'`" % executable_name, warn=True)

        # libscapi protocol
        if not external_protocol:
            cxn.run('cd %s && chmod +x %s' % (working_directory, executable_name))
            cxn.run('cd %s && ./%s partyID %s %s &' % (working_directory, executable_name, party_id, args))
        # external protocols
        else:
            # with coordinator
            if 'coordinatorConfig' in data:
                cxn.put('InstancesConfigurations/parties.conf', '%s/MATRIX' % working_directory)
                if protocol_name == 'SCALE-MAMBA':
                    cxn.put('InstancesConfigurations/public_ips', '%s/MATRIX' % working_directory)
                    cxn.put(cxn.connect_kwags.key_filename, '%s/MATRIX' % working_directory)
                if party_id == 0:
                    coordinator_executable = data['coordinatorExecutable']
                    coordinator_args = ' '.join(data['coordinatorConfig'])
                    cxn.run('./%s %s' % (coordinator_executable, coordinator_args))
                else:
                    # run the parties that depends in the coordinator
                    self.pool.run('./%s %s %s' % (executable_name, party_id - 1, args))
                    with open('Execution/execution_log.log', 'a+') as log_file:
                        log_file.write('%s\n' % args)
            else:
                # run external protocols with no coordinator
                self.pool.run('. ./%s %s %s' % (executable_name, party_id, args))
                with open('Execution/execution_log.log', 'a+') as log_file:
                    log_file.write('%s\n' % args)

    def run_protocol_profiler(self):
        pass

    def run_protocol_latency(self):
        pass

    def update_libscapi(self):
        pass

    def get_logs(self):
        pass

    def test_task(self, c, party_id):
        print(c, party_id)

