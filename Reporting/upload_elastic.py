import os
import json
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
            with open(f'{os.getcwd()}/GlobalConfigurations/awsRegions.json') as gc_file:
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
        raw_configurations = self.config_file['configurations'][0].split('@')
        # delete values, only the parameters are left
        del raw_configurations[1::2]
        raw_configurations = [rc[1:] for rc in raw_configurations]
        raw_configurations.insert(0, 'partyId')
        raw_configurations.insert(0, 'protocolName')

        dts = datetime.utcnow()
        # results_path += '/*%s*.json' % analysis_type
        results_files = glob('%s/*%s*.json' % (expanduser(results_path), analysis_type))
        for file in results_files:
            config_values = basename(file).split('*')
            # remove the json extension
            config_values[-1] = config_values[-1][:-5]
            analyzed_parameter = config_values[1].lower()
            del config_values[1]

            try:
                with open(file) as results:
                    data = json.load(results, object_pairs_hook=OrderedDict)
                    doc = OrderedDict()
                    for idx in range(len(raw_configurations)):
                        doc[raw_configurations[idx]] = config_values[idx]
                    number_of_tasks = len(data)
                    number_of_iterations = len(data[0]) - 1
                    for task_idx in range(number_of_tasks):
                        val = 0
                        for iteration_idx in range(number_of_iterations):
                            val += data[task_idx]['iteration_%s' % iteration_idx]
                        doc[data[task_idx]['name']] = val / float(number_of_iterations)
                    doc['executionTime'] = dts

                    self.es.index(index='%sresults' % analyzed_parameter, doc_type='%sresults' % analyzed_parameter,
                                  body=doc)
            except EnvironmentError:
                print('Cannot read results files')

    def upload_log_data(self, results_path):
        """
        Upload results file in log format to Elasticsearch
        :type results_path: list
        :param results_path: list of results files location
        :return:
        """
        raw_configurations = self.config_file['configurations'][0].split('@')
        del raw_configurations[1::2]
        # raw_configurations = [rc[1:] for rc in raw_configurations]
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

