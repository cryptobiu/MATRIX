# MATRIX

MATRIX is an MPC Test Automation Framework developed by developed by [Bar Ilan University Cryptography Research Group](http://crypto.biu.ac.il/).
It automates the tedious process of deploying, running, monitoring and summarizing results.
It uses AWS [spot-instances](https://aws.amazon.com/ec2/spot/), and can be used internally on a local host or in a container deployment.



## Installation
The system can be deploy on local machine, remote server or AWS machine.
MATRIX runs under python 3.5 and uses [fabric](https://github.com/fabric/fabric), [fabric3](https://pypi.python.org/pypi/Fabric3/1.10.2) and [xlsxwriter](http://xlsxwriter.readthedocs.io/).  
In order to install this three modules use pip: `pip3 install --user xlsxwriter fabric fabric3`
After the modules installed, clone this repository to install MATRIX.

### Local installation
Before you run the protocol check that the `regions` parameter set to `local` at the config [file](https://github.com/cryptobiu/MATRIX/blob/master/Configurations/Config_BMR.json)

### Servers Installation
In order to deploy MATRIX on your own server cluster, supply a file that contains servers addresses.
A sample file can be found [here](https://github.com/cryptobiu/MATRIX/blob/master/Assets/servers_file).
You will need also to change this lines at [fabfile.py](https://github.com/cryptobiu/MATRIX/blob/master/ExperimentExecute/fabfile.py):
1. Set the correct user at `env.user = 'ubuntu'`
2. Uncomment `# env.password=''` and fill your password.
3. Comment this line `env.key_filename = [expanduser('~/Keys/matrix.pem')]`

### AWS Installation
To deploy the system at your machine with your credentials, you must have AWS account and configure your security keys.  
In order to configure AWS account please read this [link](http://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/credentials.html).
After you created your AWS key, change this line at [fabfile.py](https://github.com/cryptobiu/MATRIX/blob/master/ExperimentExecute/fabfile.py):

- set the correct location of your AWS key `env.key_filename = [expanduser('~/Keys/matrix.pem')]`

### MATRIX Usage

In order to receive easy access to the MATRIX system, MATRIX uses basic CLI. To run the CLI run: `python3 main.py` 

#### ImagesDeployment


1.  [__ImagesDeployment__](https://github.com/cryptobiu/MATRIX/tree/master/ImagesDeployment): Deploy spot instances according to configuration [file](https://github.com/cryptobiu/MATRIX/blob/master/Configurations/Config_GMW.json).
2.  [__ExperimentExecute__](https://github.com/cryptobiu/MATRIX/tree/master/ExperimentExecute): Executes the protocol
3. [__ExperimentReport__](https://github.com/cryptobiu/MATRIX/tree/master/ExperimentReport): Produce Excel report with the average time of each phase of the protocol.
