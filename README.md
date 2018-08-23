# MATRIX

MATRIX is an MPC Test Automation Framework developed by [Bar Ilan University Cryptography Research Group](http://crypto.biu.ac.il/).
It automates the tedious process of deploying, running, monitoring and summarizing results.
It uses AWS [spot instances](https://aws.amazon.com/ec2/spot/), and can be used internally on a local host or in a container deployment.

The system requires a management computer (Manager) - a computer that centralized all the execution.
The Manager executes all the experiment phases, starting from install the experiment up to analyse it's results.
The Manager is a stand alone workstation and it's not part of the the workstations that participate in the experiment.

In order to use MATRIX an account at AWS is required. To create account at AWS: 
1. Sing up for [AWS](https://portal.aws.amazon.com/billing/signup#/start).   
2. Define your [credentials](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/credentials.html) at the Manager computer. 

MATRIX uses two services of AWS:
1. Spot instances - The execution of the protocols is done by deploy spot instances. All the instances have the same AMI(Amazon Machine Image).
In most cases we are using a custom AMI that contains [libscapi](https://github.com/cryptobiu/libscapi). AMI are defined per region.
If you are executing an experiment on two different regions(locations), you will need to copy the AMI to the requested regions.
More on AMI can be found [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html).
2. Elasticsearch service - The analysis done by Elasticsearch (ES). All the results are uploaded and stored at ES.
Information on ES can be found [here](https://www.elastic.co/). We are also using the built in [Kibana](https://www.elastic.co/products/kibana)
plugin to visualize our results.

Basic architecture of MATRIX:  
![alt text](../dev/Assets/BasicArchitecture.png)   

## Installation
MATRIX runs under python 3.5 and uses [fabric](https://github.com/fabric/fabric), [fabric3](https://pypi.python.org/pypi/Fabric3/1.10.2) and [openpyxl](https://openpyxl.readthedocs.io/en/stable/).  
Matrix tested on Ubuntu 16.04.3/18.04.1 LTS and CentOS 7.3.  
To install python3 and pip under Ubuntu 16.04/18.04 :

`sudo apt-get install python3 python3-pip`

To install under CentOS 7.3:

`sudo yum install python35u.x86_64 python35u-pip.noarch`

After You installed python 3 and pip3 you will need to install the modules MATRIX uses. To install this three modules use pip3

`pip3 install --user openpyxl fabric fabric3 boto3 colorama certifi elasticsearch`

**NOTE**: on some computers the following error may appear: `locale.Error: unsupported locale setting`
To fix it, run:
1. sudo apt-get clean && sudo apt-get update && sudo apt-get install -y locales
2. locale-gen en_US.UTF-8

After the modules installed, clone this repository to install MATRIX on your system.

## MATRIX Modules

### Deployment

After config file was created, You will need to deploy your images(instances). MATRIX supports three different deployments:
1. Local deployment
2. Servers deployment
3. AWS deployment

#### Local Deployment

To deploy MATRIX locally set `regions` parameter to `local` at the config [file](../master/ProtocolsConfigurations/Config_BMR.json)

#### AWS Deployment

After you created your AWS account and set your credentials, you will need a key to deploy your instances.
Detailed explanation can be found [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html).  
After you created your key, change this line at [fabfile.py](../master/ExperimentExecute/fabfile.py):

- set the correct location and name of your AWS key `env.key_filename = [expanduser('~/Keys/matrix.pem')]`

### Execution

The execution module supports these operations:
1. Pre process - Operations that need to be done before the protocol executed like installation of library.
2. Install - Install the experiment.
3. Update - Update the current experiment if change was done to his code.
4. Execute - execute the protocol.
5. Results - Collect the results file from the images and analyse them. For more details see ExperimentReport section.
6. analyse - analyse the results from given directory.

### Reporting

MATRIX analyse four parameters:

1. CPU runtime (milliseconds)
2. RAM usage (GB)
3. Sent bytes (bytes)
4. Received bytes (bytes)

The report module analyse the results files that was taken from the images by number of parties parameter.
If you want to analyse by different parameter use the Elasticsearch option.

MATRIX uses libscapi logger [API](https://github.com/cryptobiu/libscapi/blob/dev/include/infra/Measurement.hpp).  
The logging is done at the protocol code. The logger generate suitable json files for the report module.  
If you don't want to use libscapi logger API, make sure your files are at this name and format:   
`protocolName_analysedParameter_partyId=id_numOfParties=#parties.json`  
The values for analysedParameter are:

1. cpu
2. commSent
3. commReceived
4. memory

Example file can be found [here](../master/Assets/MPCHonestMajorityNoTriples_cpu_partyId=0_numOfParties=3.json)

## MATRIX Configurations

### GlobalConfigurations

In order to connect to the instances MATRIX uses a file that contains the AWS keys and security groups.
For each region in AWS you need to create an entry in the global configuration file.
Sample configuration file can be found [here](../master/GlobalConfigurations/regions.json)

### ProtocolsConfigurations
MATRIX uses configuration file to set it execution. The configuration file is written in [json](https://en.wikipedia.org/wiki/JSON) format.  
Each configuration file has the following fields:
* amis - List of AMI(s).
If using custom AWS AMI, the AMI need to be installed in all the regions that we want to test.
* protocol - Name of protocol
* numOfParties - Size of the parties
* gitAddress - Git  repository path. MATRIX will clone the repository into all target servers, configure, 
make and install. If installation of other libraries is needed to be done, see pre-process section of MATRIX for details.
* awsInstType - AWS instance type. For details about the different instance types, you can read [here](https://aws.amazon.com/ec2/instance-types/).
* awsBidPrice - Bid price for spot instances machine in USD
* executableName - The name of the executable to execute
* preProcessTask - ID of the pre process task that required.
The available pre process tasks that defines in MATRIX can be found in this [script](../master/ExperimentExecute/pre_process.py)
* Configurations - List of configurations to run. Each configuration is a set of CLI arguments to the executable.
The arguments are separated between them by '@'. Party ID is added automatically
* numOfRepetitions - How Many times MATRIX will execute the protocol
* numOfInternalRepetitions - How many times the protocol will be executed on single run.
* gitBranch - The branch the protocol uses. default value is `master`
* isPublished - Indicate if the protocol was published.
* isExternal - Indicate if the protocol external to libscapi library
* regions - AWS regions to execute the protocol.
* workingDirectory - The directory of the protocol and the data related to the protocol.
* resultsDirectory - Directory to copy to the results files from the servers. The directory is local directory at the MATRIX system computer.
* emails - MATRIX will send notifications to this email addresses. Multiple email addresses are supported
* institute - Research Group identifier
* coordinatorConfig - If coordinator exists in the protocol, the configuration for him will described here.
The configuration need to be in the same format of 'configurations' field
* coordinatorExecutable - The name of the coordinator executable


### MATRIX Usage

In order to receive easy access to the MATRIX system, MATRIX uses basic CLI. To run the CLI run: `python3 main.py`

For bugs/features requests open an issue or send mail to liork.cryptobiu@gmail.com
