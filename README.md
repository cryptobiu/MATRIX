# MATRIX

MATRIX is an MPC Test Automation Framework developed by [Bar Ilan University Cryptography Research Group](http://crypto.biu.ac.il/).
It automates the tedious process of deploying, running, monitoring and summarizing results.
It uses AWS or Scaleway to provision servers(instances), and can be used internally on a local host or in a container deployment.

The system requires a management computer (Manager) - a computer that centralized all the execution.
The Manager executes all the experiment phases, starting from install the experiment up to analyse it's results.
The Manager is a stand alone workstation and it's not part of the workstations that participate in the experiment.

In order to use all MATRIX capabilities, a cloud account is required.
MATRIX uses two cloud providers(CP):
1. AWS
2. Scaleway - for ARM computing resources

To create account at AWS: 
* Sign up for [AWS](https://portal.aws.amazon.com/billing/signup#/start).   
* Define your [credentials](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/credentials.html) at the Manager computer.

To create account at Scaleway:
* Sign up for [Scaleway](https://www.scaleway.com/)

MATRIX uses two services of AWS:
1. Spot instances - The execution of the protocols is done by deploy spot instances. All the instances have the same AMI(Amazon Machine Image).
In most cases we are using a custom AMI that contains [libscapi](https://github.com/cryptobiu/libscapi). AMI are defined per region.
If you are executing an experiment on two different regions(locations), you will need to copy the AMI to the requested regions.
More on AMI can be found [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html).
2. Elasticsearch service - The analysis done by Elasticsearch (ES). All the results are uploaded and stored at ES.
Information on ES can be found [here](https://www.elastic.co/). We are also using the built in [Kibana](https://www.elastic.co/products/kibana)
plugin to visualize our results.
  

## Installation
MATRIX runs under python 3.5 and uses [fabric](https://github.com/fabric/fabric), [fabric3](https://pypi.python.org/pypi/Fabric3/1.10.2) and [openpyxl](https://openpyxl.readthedocs.io/en/stable/).  
Matrix tested on these OSs:
* Ubuntu 16.04.3/18.04.1 LTS
* CentOS 7.3
* Arch Linux  

To install Python 3 and pip under Ubuntu 16.04/18.04 :

`sudo apt-get install python3 python3-pip`

To install under CentOS 7.3:

`sudo yum install python35u.x86_64 python35u-pip.noarch`

To install under Arch Linux:

`pacman -S python python-pip`

After You installed Python 3 and pip3 you will need to install the modules MATRIX uses. To install this three modules use pip3

`pip3 install --user openpyxl 'fabric<2.0' fabric3 boto3 colorama certifi elasticsearch scaleway-sdk`

**NOTE**: on some computers the following error may appear: `locale.Error: unsupported locale setting`
To fix it, run:
1. `sudo apt-get clean && sudo apt-get update && sudo apt-get install -y locales`
2. `locale-gen en_US.UTF-8`

After the modules installed, clone this repository to install MATRIX on your system.

## MATRIX Modules

### Deployment

After config file was created, You will need to deploy your images(instances). MATRIX supports three different deployments:
1. Local deployment
2. Servers deployment
3. AWS deployment

#### Local Deployment

To deploy MATRIX locally in `CloudProviders` let the name of the provider be `local`. An example of a local deployment configuration can be found in [here](ProtocolsConfigurations/Config_GMW.json)

#### AWS Deployment

After you created your AWS account and set your credentials, you will need a key to deploy your instances.
Detailed explanation can be found [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html).  
After you created your key, change this line at [fabfile.py](../master/ExperimentExecute/fabfile.py):

- set the correct location and name of your AWS key `env.key_filename = ['%s/Keys/matrix.pem' % Path.home()]`

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
2. RAM usage (GB) - Will be added in future release
3. Sent bytes (bytes) - Will be added in future release
4. Received bytes (bytes) - Will be added in future release

The report module analyse the results files that was taken from the images by number of parties parameter.
If you want to analyse by different parameter use the Elasticsearch option.

MATRIX uses a header class logger [API](../master/Reporting/MatrixMeasurement.h).  
The logging is done at the protocol code. The logger generate logs files that uploaded to [Elasticsearch](https://www.elastic.co/) server.  
To use MATRIX logger class, just include `MatrixMeasurement.h` to your main class.  

To measure task:
```
#include "MatrixMeasurement.h"
...
int main(int argc, char* argv[])
{
    MatrixMeasurement matrixLogger(argc,argv,vector<string>{"offline","online"}, numberOfIterations);
...
    matrixLogger.startSubTask("offline", iterationIdx);
    offline.run();
    matrixLogger.endSubTask("offline", iterationIdx);
...
}

``` 

## MATRIX Configurations

### GlobalConfigurations

In order to connect to the instances MATRIX uses a file that contains the AWS keys and security groups.
For each region in AWS you need to create an entry in the global configuration file.
Sample configuration file can be found [here](../master/GlobalConfigurations/regions.json)

### ProtocolsConfigurations
MATRIX uses configuration file to set it execution. The configuration file is written in [json](https://en.wikipedia.org/wiki/JSON) format.  
Each configuration file has the following fields:
* `protocol` - Name of protocol
* `CloudProviders` - for eac cloud provider we need to create a unique entry. each entry contains these fields:
    * `numOfParties` - number of instances to create. 
    * `instanceType`
    * `spotPrice` - relevant only to AWS. For detailed explanation about spot instances, use this [link](https://aws.amazon.com/ec2/spot/) 
    * `git`:
        * `gitAddress` - Git  repository path. MATRIX will clone the repository into all target servers, configure, make and install. 
        If installation of other libraries is needed to be done, see pre-process section of MATRIX for details. 
        NOTE: pulling this should make a build script avilable in `MATRIX/build.sh` and the executeable defined in `executableName` available in the `workingDirectory`. Otherwise, MATRIX will flip out and throw things around the room!
        * `gitBranch` - The branch the protocol uses.
        
* `executableName` - The name of the executable to execute
* `preProcessTask` - ID of the pre process task that required. Not relevant to all of the protocols.
The available pre process tasks that defines in MATRIX can be found in this [script](Execution/pre_process.py)
* `Configurations` - List of configurations to run. Each configuration is a set of CLI arguments to the executable.
The arguments are separated between them by '@'. Party ID is added automatically
* `numOfRepetitions` - How Many times MATRIX will execute the protocol
* `numOfInternalRepetitions` - How many times the protocol will be executed on single run.
* `isPublished` - Indicate if the protocol was published.
* `isExternal` - Indicate if the protocol external to libscapi library - NOTE: It is very important to set this option for any non-libscapi project or the MATRIX tool will explode and burn any small villages nearby including small furry pets living in said villages, very sad. 
* `regions` - AWS regions to execute the protocol.
* `workingDirectory` - The directory of the protocol and the data related to the protocol.
* `resultsDirectory` - Directory to copy to the results files from the servers. The directory is local directory at the MATRIX system computer.
* `emails` - MATRIX will send notifications to this email addresses. Multiple email addresses are supported
* `institute` - Research Group identifier
* `coordinatorConfig` - If coordinator exists in the protocol, the configuration for him will described here.
The configuration need to be in the same format of 'configurations' field
* `coordinatorExecutable` - The name of the coordinator executable


### MATRIX Usage

In order to receive easy access to the MATRIX system, MATRIX uses basic CLI. To run the CLI run: `python3 main.py`

For bugs/features requests open an issue or send mail to liork.cryptobiu@gmail.com
