import os
import json
from json import JSONDecodeError

import shutil
import certifi
from glob import glob
from datetime import datetime
from collections import OrderedDict
from elasticsearch import Elasticsearch
from os.path import basename, expanduser


class Elastic:
    """
    The class enables to upload results files in JSON/log format to Elasticsearch server
    """
    def __init__(self, protocol_config):
        """
        :type protocol_config str
        :param protocol_config: the configuration of the protocol we want to execute
        """
        self.config_file = protocol_config
        try:
            with open(f'{os.getcwd()}/GlobalConfigurations/tokens.json') as gc_file:
                global_config = json.load(gc_file, object_pairs_hook=OrderedDict)
        except EnvironmentError:
            print('Cannot open Global Configurations')
            return
        es_address = global_config['Elasticsearch']['address']
        self.es = Elasticsearch(es_address, ca_certs=certifi.where())

    def upload_cpu_data(self, results_files):
        """
        Upload results file in JSON format to Elasticsearch
        :type results_files list
        :param results_files: list of results files
        :return:
        """
        dts = datetime.utcnow()
        for file in results_files:
            try:
                with open(file) as results:
                    data = json.load(results, object_pairs_hook=OrderedDict)
                    doc = OrderedDict()
                    parameters = data['parameters']
                    for key, value in parameters.items():
                        doc[key] = value
                    number_of_tasks = len(data['times'])
                    number_of_iterations = len(data['times'][0]) - 1
                    for task_idx in range(number_of_tasks):
                        val = 0
                        for iteration_idx in range(number_of_iterations):
                            val += float(data['times'][task_idx]['iteration_%s' % iteration_idx])
                        doc[data['times'][task_idx]['name']] = val / float(number_of_iterations)
                    doc['executionTime'] = dts

                    self.es.index(index='cpuresults', doc_type='cpuresults', body=doc)

            except EnvironmentError:
                print(f'Cannot read results from {file}')
            except KeyError:
                print(f'Cannot read results from {file}')
            except JSONDecodeError:
                print(f'Cannot read results from {file}')
            except Exception as e:
                print(f'Cannot read results from {file}: {str(e)}')

    def upload_comm_data(self, results_files, protocol_name):
        """
        Upload results file in JSON format to Elasticsearch
        :type results_files list
        :param results_files: list of results files
        :type protocol_name str
        :param protocol_name: protocol name
        :return:
        """
        dts = datetime.utcnow()
        for file in results_files:
            with open(file) as results:
                data = json.load(results, object_pairs_hook=OrderedDict)
                doc = OrderedDict()
                doc['executionTime'] = dts
                doc['protocolName'] = protocol_name
                number_of_parties = int(data['metaData']['numberOfParties'])

                bytes_received = bytes_sent = 0
                statistics_data = data['data']
                for idx in range(number_of_parties - 1):
                    bytes_received += statistics_data[idx]['bytesReceived']
                    bytes_sent += statistics_data[idx]['bytesSent']

                doc['bytesReceived'] = bytes_received / number_of_parties
                doc['bytesSent'] = bytes_sent / number_of_parties
                doc['partyId'] = data['metaData']['partyId']
                doc['numberOfParties'] = number_of_parties
                self.es.index(index='commresults', doc_type='commresults', body=doc)

    def upload_log_data(self, results_path):
        """
        Upload results file in log format to Elasticsearch
        :type results_path: list
        :param results_path: list of results files location
        :return:
        """
        raw_configurations = self.config_file['configurations'][0].split('@')
        del raw_configurations[1::2]
        raw_configurations.insert(0, 'partyId')
        raw_configurations.insert(0, 'protocolName')

        dts = datetime.utcnow()
        results_files = glob('%s/*.log' % expanduser(results_path))
        protocol_name = self.config_file['protocol']
        try:
            for file in results_files:
                config_values = basename(file).split('*')
                config_values[-1] = config_values[-1][:-4]
                config_values.insert(0, protocol_name)

                with open(file) as results:
                    doc = OrderedDict()
                    for idx in range(len(raw_configurations)):
                        doc[raw_configurations[idx]] = config_values[idx]
                    data = results.read().split('\n')
                    for d in data:
                        if len(d) > 1:
                            key = d.split(':')[0]
                            values = list(map(int, d.split(':')[1].split(',')[:-1]))  # remove the last ',' to map
                            doc[key] = sum(values) / len(values)
                    doc['executionTime'] = dts

                    self.es.index(index='cpuresults', doc_type='cpuresults', body=doc)

        except EnvironmentError:
            print('Cannot read results files')

    def upload_all_data(self, results_dir, protocol_name):
        """
        Activate the relevant function according to the results files format
        :return:
        """
        comm_base_path = f'{results_dir}/commData'
        comm_files = glob(expanduser(f'{results_dir}/*Comm*.json'))
        os.makedirs(comm_base_path, exist_ok=True)

        for file in comm_files:
            shutil.move(file, comm_base_path)

        cpu_files = glob(expanduser(f'{results_dir}/*.json'))
        comm_files = glob(expanduser(f'{comm_base_path}/*.json'))

        # os.makedirs(f'WebApp/ReportingLogs/', exist_ok=True)
        # with open(f'WebApp/ReportingLogs/{protocol_name}.log', 'w+') as output_file:
        #     print('Upload log files to the DB', file=output_file)

        self.upload_cpu_data(cpu_files)
        self.upload_comm_data(comm_files, protocol_name)
        # with open(f'WebApp/ReportingLogs/{protocol_name}.log', 'w+') as output_file:
        #     print('all log files uploaded to the DB', file=output_file)

