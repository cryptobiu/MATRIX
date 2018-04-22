import os
import sys
import json
import boto3
from collections import OrderedDict
from shutil import copyfile
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


def manipulate_spdz2_networking():
    # write the public ips
    public_ips_file = 'InstancesConfigurations/public_ips'
    with open(public_ips_file, 'r') as ips_file:
        origin_data = ips_file.readlines()
        coordinator_ip = origin_data[-1]
        origin_data.insert(0, coordinator_ip)
        del origin_data[-1]
    os.remove(public_ips_file)
    with open(public_ips_file, 'w+') as new_ips_file:
        new_ips_file.writelines(origin_data)

    # write gf2n parties file
    copyfile('InstancesConfigurations/parties.conf', 'InstancesConfigurations/Parties_gf2n.txt')

    # write gfp parties file
    with open('InstancesConfigurations/parties.conf', 'r') as parties_file:
        parties_data = parties_file.readlines()
        parties_data = [port.replace('8000', '9000') for port in parties_data]
        with open('InstancesConfigurations/Parties_gfp.txt', 'w+') as gfp_file:
            gfp_file.writelines(parties_data)

    # write the local ip of the host to the configuration file
    with open('ProtocolsConfigurations/Config_SPDZ.json', 'r') as json_file:
        json_data = json.load(json_file, object_pairs_hook=OrderedDict)
        for host in range(len(json_data['configurations'])):
            host_idx_start = json_data['configurations']['configuration_%s' % host].index('@-h') + 4
            host_idx_end = json_data['configurations']['configuration_%s' % host].index('@partyid@')
            old_host = (json_data['configurations']['configuration_%s' % host][host_idx_start:host_idx_end])
            new_host_public_ip = old_host
            client = boto3.client('ec2', region_name='us-east-1')
            response = client.describe_instances(Filters=[{
                'Name': 'network-interface.association.public-ip',
                'Values': [new_host_public_ip]
            }])
            new_host_private_ip = response['Reservations'][0]['Instances'][0]['PrivateIpAddress']
            json_data['configurations']['configuration_%s' % host] =\
                json_data['configurations']['configuration_%s' % host][:host_idx_start] + new_host_private_ip + \
                json_data['configurations']['configuration_%s' % host][host_idx_end + 1:]

    with open('ProtocolsConfigurations/Config_SPDZ.json', 'w') as new_json_file:
        json.dump(json_data, new_json_file, indent=2)


task_name = sys.argv[1]

if task_name == '1':
    install_ntl()
elif task_name == '2':
    install_malicious_yao_lib()
elif task_name == '3':
    install_spdz_stations()
elif task_name == '4':
    manipulate_spdz2_networking()
else:
    raise ValueError('Invalid choice')
