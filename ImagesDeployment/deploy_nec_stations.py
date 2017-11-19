from fabric.api import *

env.hosts = ['132.71.147.104', '132.71.147.37', '132.71.147.55']
env.user = 'user'
env.password = 'user'


@task
def install_spdz():
    sudo('apt-get update')
    sudo('apt-get install git -y')
    sudo('apt-get install autoconf -y')
    sudo('apt-get install libtool -y')
    sudo('apt-get install yasm m4 build-essential unzip wget -y')

    sudo('mkdir -p mpir')

    with cd('mpir'):
        sudo('wget http://mpir.org/mpir-3.0.0-alpha2.zip')
        sudo('unzip mpir-3.0.0-alpha2.zip')
        with cd('mpir-3.0.0'):
            sudo('./configure --enable-cxx')
            sudo('make')
            sudo('make check')
            sudo('make install')
            sudo('ln -s /usr/local/lib/libmpir.so.23 /usr/lib/')
            sudo('ln -s /usr/local/lib/libmpirxx.so.8 /usr/lib/')
    run('git clone https://github.com/jedisct1/libsodium.git')

    with cd('libsodium'):
        sudo('autoreconf -i')
        sudo('./configure')
        sudo('make && make check')
        sudo('make install')
        sudo('ln -s /usr/local/lib/libsodium.so.23 /usr/lib/')

    sudo('rm -rf SPDZ-2G')
    run('git clone https://liorbiu:4aRotdy0vOhfvVgaUaSk@github.com/cryptobiu/SPDZ-2.git')
    with cd('SPDZ-2'):
        sudo('make')
        sudo('bash Scripts/setup-online.sh')
        sudo('python compile.py tutorial')
        sudo('bash Scripts/run-online.sh tutorial')

    sudo('rm -rf NECMIX')
    run('git clone https://liorbiu:4aRotdy0vOhfvVgaUaSk@github.com/cryptobiu/NECMIX.git')
    with cd('NECMIX'):
        sudo('apt-get install libssl-dev -y')
        run('make')
