import os
import json
import certifi
from glob import glob
from os.path import basename
from datetime import datetime
from collections import OrderedDict
from elasticsearch import Elasticsearch


class Elastic:
    def __init__(self, conf_file):
        self.config_file_path = conf_file
        self.es = Elasticsearch('https://search-escryptobiu-fyopgg3zepk6dtda4zerc53apy.us-east-1.es.amazonaws.com/',
                                use_ssl=True, ca_certs=certifi.where())

    def delete_index(self, index_name):
        self.es.indices.delete(index_name)

    def create_index(self):
        request_body = \
            {
                'mappings':
                {
                    'memoryresults':
                    {
                        'properties':
                            {
                                'partiesNumber': {'type': 'integer'},
                                'partyId': {'type': 'integer'},
                                'protocolName': {'type': 'text'},
                                'executionTime': {'type': 'date'}
                            }
                    }
                }
            }
        self.es.indices.create(index='memoryresults', body=request_body)

    def upload_data(self, analysis_type, results_path):

        with open(self.config_file_path) as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)
            raw_configurations = list(data['configurations'].values())[0].split('@')
            del raw_configurations[1::2]
            raw_configurations = [rc[1:] for rc in raw_configurations]
            raw_configurations.insert(0, 'partyId')
            raw_configurations.insert(0, 'protocolName')

        dts = datetime.utcnow()
        results_files = glob('%s/*%s*.json' % (results_path, analysis_type))
        for results_file in results_files:
            config_values = basename(results_file).split('*')
            config_values[-1] = config_values[-1][:-5]
            analyzed_parameter = config_values[1].lower()
            del config_values[1]

            with open(results_file) as results:
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

    def upload_data(self):
        results_path = input('Enter results directory. current path is: %s): ' % os.getcwd())
        self.upload_data('cpu', results_path)
        self.upload_data('commReceived', results_path)
        self.upload_data('commSent', results_path)
        self.upload_data('memory', results_path)
