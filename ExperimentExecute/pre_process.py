import os
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


task_name = input('Enter task Name:\n'
                  '1. Install NTL-9.10.0'
                  '2. Install Malicious Yao Batch library')

if task_name == '1':
    install_ntl()
elif task_name == '2':
    install_malicious_yao_lib()
else:
    raise ValueError('Invalid choice')
