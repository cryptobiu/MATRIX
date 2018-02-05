import os
import sys
from os.path import expanduser


def install_ntl():
    os.system('wget http://www.shoup.net/ntl/ntl-9.10.0.tar.gz')
    os.system('tar -xf ntl-9.10.0.tar.gz')
    os.chdir('ntl-9.10.0/src')
    os.system('./configure WIZARD=off CXXFLAGS=\"-g -O3 -fPIC\"')
    os.system('make')


def install_malicious_yao_lib():
    os.chdir(expanduser('~/libscapi/protocols/MaliciousYaoBatch/lib'))
    os.system('make')


def install_mpir():
    # delete directory if exists
    os.system('rm -rf mpir-3.0.0')
    os.system('wget http://mpir.org/mpir-3.0.0.tar.bz2')
    os.system('tar -xf mpir-3.0.0-alpha2.tar.bz2')
    os.chdir('mpir-3.0.0/')
    os.system('./configure --enable-cxx')
    os.system('make')
    os.system('make check')
    os.system('sudo make install')


def install_spdz_stations():
    os.system('sudo apt-get update')
    os.system('sudo apt-get install build-essential -y')
    os.system('sudo apt-get install cmake libgmp3-dev yasm m4 python libz-dev libsodium-dev -y')

    # Install dependencies of SPDZ

    install_mpir()
    install_ntl()

    # Install libscapi
    os.chdir(expanduser('~'))
    os.system('git clone https://github.com/cryptobiu/libscapi.git')
    os.chdir(expanduser('~/libscapi'))
    os.system('git checkout SPDZ')
    os.system('make')

    # Install MPCHonestMajorityForSpdz
    os.chdir(expanduser('~'))
    os.system('git clone https://github.com/cryptobiu/MPCHonestMajorityForSpdz.git')
    os.chdir(expanduser('~/MPCHonestMajorityForSpdz'))
    os.system('cmake .')
    os.system('make')

    # Install SPDZ-2_extension_library
    os.chdir(expanduser('~'))
    os.system('git clone https://github.com/cryptobiu/spdz-2_extension_library')
    os.chdir(expanduser('~/spdz-2_extension_library'))
    os.system('cmake .')
    os.system('make')

    # Install SPDZ-2
    os.chdir(expanduser('~'))
    os.system('git clone https://github.com/cryptobiu/SPDZ-2')
    os.chdir(expanduser('~/SPDZ-2'))
    os.system('make')


task_name = sys.argv[1]

if task_name == '1':
    install_ntl()
elif task_name == '2':
    install_malicious_yao_lib()
elif task_name == '3':
    install_spdz_stations()
else:
    raise ValueError('Invalid choice')
