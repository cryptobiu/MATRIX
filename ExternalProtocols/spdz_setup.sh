#!/bin/bash

########################################################################################
show_usage() {
	echo $0" OPTIONS"
	echo "-x			Use SPDZ extension library"
	echo "-h			Show usage help and exit"
}

########################################################################################
while getopts p:i:n:s:xh option
do
 case "${option}"
 in
 h) show_usage; exit 0;;
 x) EXT=on;;
 esac
done

########################################################################################

if [ -n "$EXT" ]
then
	echo "using SPDZ extension"
else
	echo "NOT using SPDZ extension"
fi

########################################################################################

cd ~
git clone https://ran-proshan:GitHub1@github.com/cryptobiu/SPDZ-2.git

if [ -n "$EXT" ]
then
	git clone https://ran-proshan:GitHub1@github.com/cryptobiu/MPCHonestMajorityForSpdz.git
	cd ./MPCHonestMajorityForSpdz
	make clean
	cmake .
	make
	cd ..

	git clone https://ran-proshan:GitHub1@github.com/cryptobiu/spdz-2_extension_library.git
	cd ./spdz-2_extension_library
	make clean
	cmake .
	make
	cd ..
	export SPDZ_EXT_LIB=~/spdz-2_extension_library/libspdz_ext_biu.so

	mv ./SPDZ-2/CONFIG ./SPDZ-2/CONFIG.orig
	mv ./SPDZ-2/CONFIG_extended ./SPDZ-2/CONFIG
fi

cd ./SPDZ-2
make clean
make

########################################################################################


