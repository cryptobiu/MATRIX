#!/bin/bash

########################################################################################
show_usage() {
	echo $0" OPTIONS"
	echo "-i <pid>		The party identity number"
	echo "-n <prts>		The number of parties"
	echo "-s			Server IP address"
	echo "-p			Port number"
	echo "-x			Use SPDZ extension library"
	echo "-h			Show usage help and exit"
}

########################################################################################
while getopts i:n:s:p:xh option
do
 case "${option}"
 in
 i) PID=$OPTARG;;
 n) PARTIES=${OPTARG};;
 s) SRVR=$OPTARG;;
 p) PORT=$OPTARG;;
 x) EXT=on;;
 h) show_usage; exit 0;;
 esac
done

########################################################################################
re='^[0-9]+$'

if ! [[ $PID =~ $re ]]
then
	echo "Party identity is mandatory"; exit 1
else
	echo "Party identity = "$PID
fi

if ! [[ $PARTIES =~ $re ]]
then
	echo "Parties number is mandatory"; exit 1
else
	echo "Number of parties = "$PARTIES
fi

if [ -n "$EXT" ]
then
	echo "using SPDZ extension"
	BITSP=61
else
	echo "NOT using SPDZ extension"
	BITSP=64
fi

echo "Server IP address "$SRVR

if [ -z "$PORT" ]
then
	PORT=8000
fi
echo "Using port number "$PORT

########################################################################################

cd ./SPDZ-2

if [ $PARTIES == $PID ]
then
	./Server.x $PARTIES $PORT
else
    cp ~/parties.conf ~/SPDZ-2/Parties_gfp.txt

    ./compile.py ubi_gfp_mult

    sleep 10
	INPUT=$(($PID+3))
	echo ${INPUT} | ./Player-Online.x -lgp $BITSP -h $SRVR -pn $PORT $PID ubi_gfp_mult
fi

########################################################################################


