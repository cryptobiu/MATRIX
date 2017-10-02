# MATRIX

MATRIX is a system for running Secure Multi Party Communication (MPC) protocols under AWS.  
The system relies on implementation of protocols under [libscapi](https://github.com/cryptobiu/libscapi) API.

MATRIX was developed by [Bar Ilan University Cryptography Research Group](http://crypto.biu.ac.il/).  
MATRIX runs under python 3.5 and uses [fabric](https://github.com/fabric/fabric), [fabric3](https://pypi.python.org/pypi/Fabric3/1.10.2) and [xlsxwriter](http://xlsxwriter.readthedocs.io/).  
In order to install this three modules use pip: `pip3 install --user xlsxwriter fabric fabric3` 
 

### MATRIX Modules

1.  [__ImagesDeployment__](https://github.com/cryptobiu/MATRIX/tree/master/ImagesDeployment): Deploy spot instances according to configuration[file](https://github.com/cryptobiu/MATRIX/blob/master/config.json).
2.  [__ExperimentExecute__](https://github.com/cryptobiu/MATRIX/tree/master/ExperimentExecute): Executes the protocol
3. [__ExperimentReport__](https://github.com/cryptobiu/MATRIX/tree/master/ExperimentReport): Produce Excel report with the average time of each phase of the protocol.