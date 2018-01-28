#!/bin/bash

########################################################################################
show_usage() {
	echo $0" OPTIONS"
	echo "-partyID <pid>		The party identity number"
	echo "-n <prts>		The number of parties"
	echo "-x			Use SPDZ extension library"
	echo "-p			Port number"
	echo "-h			Show usage help and exit"
}

########################################################################################
while getopts p:i:n:xh option
do
 case "${option}"
 in
 h) show_usage; exit 0;;
 x) EXT=on;;
 n) PARTIES=${OPTARG};;
 partyID) PID=$OPTARG;;
 p) PORT=$OPTARG;;
 esac
done

########################################################################################
re='^[0-9]+$'
if ! [[ $PARTIES =~ $re ]]
then
	echo "Parties number is mandatory"; exit 1
else
	echo "Number of parties = "$PARTIES
fi

if ! [[ $PID =~ $re ]]
then
	echo "Party identity is mandatory"; exit 1
else
	echo "Party identity = "$PID
fi

if [ -n "$EXT" ]
then
	echo "using SPDZ extension"
else
	echo "NOT using SPDZ extension"
fi

if [ -z "$PORT" ]
then
	PORT=38765
fi
echo "Using port number "$PORT

########################################################################################

cd ~

########################################################################################
git clone https://ran-proshan:GitHub1@github.com/cryptobiu/SPDZ-2.git

if [ -n "$EXT" ]
then
	git clone https://github.com/cryptobiu/MPCHonestMajorityForSpdz.git
	cd ./MPCHonestMajorityForSpdz
	make clean
	cmake .
	make
	cd ..

	git clone https://github.com/cryptobiu/spdz-2_extension_library.git
	cd ./spdz-2_extension_library
	make clean
	cmake .
	make
	cd ..
	export SPDZ_EXT_LIB=~/spdz-2_extension_library/libspdz_ext_biu.so

	mv ./SPDZ-2/CONFIG ./SPDZ-2/CONFIG.orig
	mv ./SPDZ-2/CONFIG_extended ./SPDZ-2/CONFIG

	BITSP=61
else
	BITSP=64
fi

cd ./SPDZ-2
make clean
make

Scripts/setup-online.sh $PARTIES $BITSP 40

./compile.py ubi_gfp_mult

if [ $PARTIES == $PID ]
then
	./Server.x 2 $PORT
else
	INPUT=$(($PID+3))
	echo $INPUT | ./Player-Online.x -lgp $BITSP -pn $PORT $PID ubi_gfp_mult
fi

########################################################################################


