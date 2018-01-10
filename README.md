# MATRIX

MATRIX is an MPC Test Automation Framework developed by [Bar Ilan University Cryptography Research Group](http://crypto.biu.ac.il/).
It automates the tedious process of deploying, running, monitoring and summarizing results.
It uses AWS [spot instances](https://aws.amazon.com/ec2/spot/), and can be used internally on a local host or in a container deployment.


## Installation
The system can be deploy on local machine, remote server or AWS machine.
MATRIX runs under python 3.5 and uses [fabric](https://github.com/fabric/fabric), [fabric3](https://pypi.python.org/pypi/Fabric3/1.10.2) and [xlsxwriter](http://xlsxwriter.readthedocs.io/).
Matrix tested on Ubuntu 16.04.3 LTS and CentOS 7.3.
To install python3 and pip under Ubuntu 16.04 :

`sudo apt-get install python3 python3-pip`

To install under CentOS 7.3:

`sudo yum install python35u.x86_64 python35u-pip.noarch`

After You installed python 3 and pip3 you will need to install the modules MATRIX uses. To install this three modules use pip3

`pip3 install --user xlsxwriter fabric fabric3`

After the modules installed, clone this repository to install MATRIX on your system.

##MATRIX Modules

### Configurations
MATRIX uses configuration file to set it execution. The configuration file is written in [json](https://en.wikipedia.org/wiki/JSON) format.  
Each configuration file has the following fields:
* protocol - Name of protocol
* amis - AWS only. Specify AMI in case pre-defined software is installed. For most cases this is not required, as can be installed in build script
if empty, will use default AWS AMI
If using custom AWS AMI, the AMI need to be installed in all the regions that we want to test. 
* numOfParties - Size of the parties
* awsInstType - AWS instance type. For details about the different instance types, you can read [here](https://aws.amazon.com/ec2/instance-types/).
* awsBidPrice - Bid price for spot instances machine in USD
* network - Type of network :local or public
* executableName - The name of the executable to execute
* Configurations - List of configurations to run. Each configuration is a set of CLI arguments to the executable. The arguments are separated between them by '@'. Party ID is added automatically
* numOfRepetitions - How Many times MATRIX will execute the protocol
* numOfInternalRepetitions - How many times the protocol will be executed on single run.
* gitAddress -  Git path. MATRIX will clone the repository into all target servers, configure, make and install. the process for building and installing is under the protocol developers control. If installation need to be done, see pre-process section of MATRIX
* gitBranch - Git branch the protocol uses. default value is `master`
* isPublished - Indicate if the protocol was published.
* regions - AWS regions to execute the protocol.
* workingDirectory - The directory of the protocol and the data related to the protocol.
* resultsDirectory - Directory to copy to the results files from the servers. The directory is local directory at the MATRIX system computer.
* emails - MATRIX will send notifications to this email addresses. Multiple email addresses are supported
* coordinatorConfig - If coordinator exists in the protocol, the configuration for him will described here. The configuration need to be in the same format of 'configurations' field
* coordinatorExecutable - The name of the coordinator executable
* institute - Research Group identifier

### ImagesDeployment

After config file was created, You will need to deploy your images(instances). MATRIX supports three different deployments:
1. Local deployment
2. Servers deployment
3. AWS deployment

#### Local Deployment
To deploy MATRIX locally set `regions` parameter to `local` at the config [file](../blob/master/Configurations/Config_BMR.json)

#### Servers Deployment
To deploy MATRIX on your own server cluster, supply a file that contains servers addresses.
A sample file can be found [here](../blob/master/Assets/servers_file).
You will need also to change this lines at [fabfile.py](../blob/master/ExperimentExecute/fabfile.py):
1. Set the correct user at `env.user = 'ubuntu'`
2. Uncomment `# env.password=''` and fill your password.
3. Comment this line `env.key_filename = [expanduser('~/Keys/matrix.pem')]`

#### AWS Deployment
To deploy MATRIX at your machine with your credentials, you must have AWS account and configure your security keys.  
In order to configure AWS account please read this [link](http://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/credentials.html).
After you created your AWS key, change this line at [fabfile.py](../blob/master/ExperimentExecute/fabfile.py):

- set the correct location of your AWS key `env.key_filename = [expanduser('~/Keys/matrix.pem')]`

### ExperimentExecute

The execution module supports these operations:
1. Pre process - Operations that need to be done before the protocol executed like installation of library.
2. Install - Install the experiment.
3. Update - Update the current experiment if change was done to his code.
4. Execute - execute the protocol.
5. Results - Collect the results file from the images and analyze them. For more details see ExperimentReport section.
6. Analyze - Analyze the results from given directory.

### ExperimentReport

The report module analyze the results files that was taken from the images. MATRIX analyze four parameters:
1. CPU runtime(milliseconds)
2. RAM usage (GB)
3. Sent bytes (bytes)
4. Received bytes (bytes)

MATRIX uses libscapi logger [API](https://github.com/cryptobiu/libscapi/blob/dev/include/infra/Measurement.hpp).  
The logging is done at the protocol code. The logger generate suitable json files for the report module.  
If you don't want to use libscapi logger API, make sure your files are at this name and format:   
`protocolName_analyzedParameter_partyId=id_numOfParties=#parties.json`  
Example file can be found [here](../blob/master/Assets/MPCHonestMajorityNoTriples_cpu_partyId=0_numOfParties=3.json)


### MATRIX Usage

In order to receive easy access to the MATRIX system, MATRIX uses basic CLI. To run the CLI run: `python3 main.py` 
