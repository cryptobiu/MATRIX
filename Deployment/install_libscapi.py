import os
from pathlib import Path

os.system('sudo apt-get update')
os.system('sudo apt-get install -y git build-essential')
os.system('sudo apt-get install -y libssl-ocaml-dev libssl-dev')
os.system('sudo apt-get install -y libgmp3-dev cmake')
os.system('sudo apt-get install gcc-6 g++-6 -y')
os.system('sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-6 60 --slave '
          '/usr/bin/g++ g++ /usr/bin/g++-6')

# Install boost 1.64
os.system('wget -O boost_1_64_0.tar.bz2 '
          'http://sourceforge.net/projects/boost/files/boost/1.64.0/boost_1_64_0.tar.bz2/download')
os.system('tar --bzip2 -xf boost_1_64_0.tar.bz2')
os.chdir('%s/boost_1_64_0' % Path.home())
os.system('./bootstrap.sh')
os.system('./b2 -j 8')  # compile boost with threads

# Install libscapi
os.chdir(str(Path.home()))
os.system('git clone https://github.com/cryptobiu/libscapi.git')
os.chdir('%s/libscapi' % Path.home())
os.system('git checkout dev')
os.system('make')
