from fabric.api import *
from os.path import expanduser, exists

env.hosts = ['54.144.43.65', '54.165.223.57']
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
