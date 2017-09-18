import json

from fabric.api import *
from fabric.contrib.files import exists
from os.path import expanduser, exists

env.hosts = open('public_ips', 'r').read().splitlines()
env.user = 'ubuntu'
env.key_filename = [expanduser('~/Keys/matrix.pem')]


@task
def install_git_project(experiment_name, git_branch):

    if not exists('/home/ubuntu/%s' % experiment_name):
        run('git clone https://liorbiu:4aRotdy0vOhfvVgaUaSk@github.com/cryptobiu/%s.git' % experiment_name)
    #
    with cd('%s' % experiment_name):
        run('git checkout %s ' % git_branch)
        run('cmake .')
        run('make')


@task
def update_git_project(experiment_name, git_branch):

    if not exists('/home/ubuntu/%s' % experiment_name):
        run('git update https://liorbiu:4aRotdy0vOhfvVgaUaSk@github.com/cryptobiu/%s.git' % experiment_name)
    #
    with cd('%s' % experiment_name):
        run('git checkout %s ' % git_branch)
        run('rm -rf CMakeFiles CMakeCahche.txt')
        run('cmake .')
        run('make')


@task
def pre_process(experiment_name):
    with cd('/home/ubuntu/%s' % experiment_name):
        if exists('pre_process.py'):
            run('python 3 pre_process.py')


@task
def run_protocol():
    with open('config.json') as data_file:
        data = json.load(data_file)
        protocol_name = data['protocol']
        executable_name = data['executableName']
        configurations = data['configurations']
        number_of_parties = data['numOfParties']

        for i in range(len(configurations)):
            print(str(configurations['conf_%s' % i]).split('-'))

        party_id = env.hosts.index(env.host)
        with cd('/home/ubuntu/%s/' % protocol_name):
            put('parties.conf', run('pwd'))

            run('./%s %s %s parties.conf' % (executable_name, party_id, number_of_parties))


