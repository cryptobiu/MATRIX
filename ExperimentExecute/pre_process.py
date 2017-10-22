import os

os.system('wget http://www.shoup.net/ntl/ntl-9.10.0.tar.gz')
os.system('tar -xf ntl-9.10.0.tar.gz')
os.chdir('ntl-9.10.0/src')
os.system('./configure')
os.system('make')