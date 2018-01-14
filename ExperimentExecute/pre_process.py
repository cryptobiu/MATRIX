import os
import sys
from os.path import expanduser


def install_ntl():
    os.system('wget http://www.shoup.net/ntl/ntl-9.10.0.tar.gz')
    os.system('tar -xf ntl-9.10.0.tar.gz')
    os.chdir('ntl-9.10.0/src')
    os.system('./configure')
    os.system('make')


def install_malicious_yao_lib():
    os.chdir(expanduser('~/libscapi/protocols/MaliciousYaoBatch/lib'))
    os.system('make')


def install_mpir():
    os.system('sudo apt-get install yasm m4 build-essential unzip wget -y')
    os.system('rm -rf mpir-3.0.0')
    os.system('wget http://mpir.org/mpir-3.0.0-alpha2.zip')
    os.system('unzip mpir-3.0.0-alpha2.zip')
    os.chdir('mpir-3.0.0/')
    os.system('./configure --enable-cxx')
    os.system('make')
    os.system('make check')
    os.system('sudo make install')


task_name = sys.argv[1]

if task_name == '1':
    install_ntl()
elif task_name == '2':
    install_malicious_yao_lib()
elif task_name == '3':
    install_mpir()
else:
    raise ValueError('Invalid choice')
