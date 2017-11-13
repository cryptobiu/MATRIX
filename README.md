# MATRIX

MATRIX is a system for running Secure Multi Party Communication (MPC) protocols under AWS.  
The system relies on implementation of protocols under [libscapi](https://github.com/cryptobiu/libscapi) API.

MATRIX was developed by [Bar Ilan University Cryptography Research Group](http://crypto.biu.ac.il/).  
MATRIX runs under python 3.5 and uses [fabric](https://github.com/fabric/fabric), [fabric3](https://pypi.python.org/pypi/Fabric3/1.10.2) and [xlsxwriter](http://xlsxwriter.readthedocs.io/).  
In order to install this three modules use pip: `pip3 install --user xlsxwriter fabric fabric3`

In order to receive easy access to the MATRIX system, MATRIX uses basic CLI. To run the CLI run: `python3 main.py`
 

### MATRIX Modules

1.  [__ImagesDeployment__](https://github.com/cryptobiu/MATRIX/tree/master/ImagesDeployment): Deploy spot instances according to configuration [file](https://github.com/cryptobiu/MATRIX/blob/master/Configurations/Config_GMW.json).
2.  [__ExperimentExecute__](https://github.com/cryptobiu/MATRIX/tree/master/ExperimentExecute): Executes the protocol
3. [__ExperimentReport__](https://github.com/cryptobiu/MATRIX/tree/master/ExperimentReport): Produce Excel report with the average time of each phase of the protocol.

To deploy the system at your machine with your credentials, you must have AWS account and configure your security keys.  
In order to configure AWS account please read this [link](http://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/credentials.html).
After you created your AWS key, run `ssh-add [key_path]/[key_name].pem`. 
