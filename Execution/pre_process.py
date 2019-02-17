import os
import sys
import json
import boto3
from collections import OrderedDict
from shutil import copyfile
from pathlib import Path

def install_java_maven():
    os.system('sudo apt-get update')
    os.system('sudo apt-get install -y openjdk-11-jdk maven')

def install_ntl():
    os.system('wget http://www.shoup.net/ntl/ntl-9.10.0.tar.gz')
    os.system('tar -xf ntl-9.10.0.tar.gz')
    os.chdir('ntl-9.10.0/src')
    os.system('./configure WIZARD=off CXXFLAGS=\"-g -O3 -fPIC\"')
    os.system('make')


def install_malicious_yao_lib():
    os.chdir('%s/libscapi/protocols/MaliciousYaoBatch/lib' % Path.home())
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
    os.chdir(str(Path.home()))
    os.system('git clone https://github.com/cryptobiu/libscapi.git')
    os.chdir('%s/libscapi' % Path.home())
    os.system('git checkout SPDZ')
    os.system('make')

    # Install MPCHonestMajorityForSpdz
    os.chdir(str(Path.home()))
    os.system('git clone https://github.com/cryptobiu/MPCHonestMajorityForSpdz.git')
    os.chdir('%s/MPCHonestMajorityForSpdz' % Path.home())
    os.system('cmake .')
    os.system('make')

    # Install SPDZ-2_extension_library
    os.chdir(str(Path.home()))
    os.system('git clone https://github.com/cryptobiu/spdz-2_extension_library')
    os.chdir('%s/spdz-2_extension_library' % Path.home())
    os.system('cmake .')
    os.system('make')

    # Install SPDZ-2
    os.chdir(str(Path.home()))
    os.system('git clone https://github.com/cryptobiu/SPDZ-2')
    os.chdir('%s/SPDZ-2' % Path.home())
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


def manipulate_spdz2_networking_multi_region():
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
    for party_idx in range(0, 50):
        os.makedirs('InstancesConfigurations/multi_regions/party%s' % party_idx)
        f1_name = 'InstancesConfigurations/parties%s.conf' % party_idx
        f2_name = 'InstancesConfigurations/multi_regions/party%s/Parties_gf2n.txt' % party_idx
        copyfile(f1_name, f2_name)

    # write gfp parties file
    for party_idx in range(0, 50):
        with open('InstancesConfigurations/parties%s.conf' % party_idx, 'r') as parties_file:
            parties_data = parties_file.readlines()
            parties_data = [port.replace('8000', '9000') for port in parties_data]
            with open('InstancesConfigurations/multi_regions/party%s/Parties_gfp.txt' % party_idx, 'w+') as gfp_file:
                gfp_file.writelines(parties_data)


def create_inputs_for_mpcfromsd():
    with open('%s/MPCFromSD/inputs9.txt' % Path.home()) as input_file:
        inputs = input_file.readlines()
        for i in range(10, 128):
            with open('%s/MPCFromSD/inputs%s.txt' % (Path.home(), i), 'w+') as new_input:
                new_input.writelines(inputs)


def create_inputs_for_statistics():
    inputs_size = [400000, 200000, 133332, 100000, 80000, 66666, 57142, 50000, 44444, 40000, 36362, 33332, 30768, 28570,
                   26666]
    for idx in range(len(inputs_size)):
        with open('%s/Secret-Sharing/inputs%s.txt' % (Path.home(), inputs_size[idx]), 'w+') as input_file:
            for idx2 in range(inputs_size[idx]):
                input_file.write('1\n')


task_name = sys.argv[1]

if task_name == '1':
    install_ntl()
elif task_name == '2':
    install_malicious_yao_lib()
elif task_name == '3':
    install_spdz_stations()
elif task_name == '4':
    manipulate_spdz2_networking()
elif task_name == '5':
    manipulate_spdz2_networking_multi_region()
elif task_name == '6':
    create_inputs_for_mpcfromsd()
elif task_name == '7':
    create_inputs_for_statistics()
elif task_name == '8':
    install_java_maven()
else:
    raise ValueError('Invalid choice')
