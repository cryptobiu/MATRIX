import os
import json
from json import JSONDecodeError

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

    def upload_json_data(self, analysis_type, results_path):
        """
        Upload results file in JSON format to Elasticsearch
        :type analysis_type str
        :param analysis_type: currently the analysis supports only CPU
        :type results_path list
        :param results_path: list of results files location
        :return:
        """
        dts = datetime.utcnow()
        results_files = glob(expanduser(f'{results_path}/*.json'))
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

                    self.es.index(index=f'{analysis_type}results', doc_type=f'{analysis_type}results', body=doc)

            except EnvironmentError:
                print(f'Cannot read results from {file}')
            except JSONDecodeError:
                print(f'Problem reading data from {file}')

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

    def upload_all_data(self):
        """
        Activate the relevant function according to the results files format
        :return:
        """
        is_external = json.loads(self.config_file['isExternal'].lower())
        results_path = self.config_file['resultsDirectory']
        if not is_external:
            self.upload_json_data('cpu', results_path)
        else:
            self.upload_log_data(results_path)

