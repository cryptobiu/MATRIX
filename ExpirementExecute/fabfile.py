from fabric.api import *
from fabric.contrib.files import exists
from os.path import expanduser, exists

env.hosts = open('public_ips', 'r').readlines()
env.user = 'ubuntu'
env.key_filename = [expanduser('~/Keys/matrix.pem')]


@task
def install_git_project(experiment_name, git_branch):

    if not exists('/home/ubuntu/%s' % experiment_name):
        run('git clone https://github.com/cryptobiu/%s.git' % experiment_name)
    #
    with cd('%s' % experiment_name):
        run('git checkout %s ' % git_branch)
        run('cmake .')
        run('git pull')
        run('make')


@task
def pre_process(experiment_name):
    with cd('/home/ubuntu/%s' % experiment_name):
        if exists('pre_process.py'):
            run('python 3 pre_process.py')
