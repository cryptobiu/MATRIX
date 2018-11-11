import os
import json
import certifi
from glob import glob
from os.path import basename, expanduser
from datetime import datetime
from collections import OrderedDict
from elasticsearch import Elasticsearch


class Elastic:
    def __init__(self, conf_file):
        self.config_file = conf_file
        self.es = Elasticsearch('https://search-escryptobiu-fyopgg3zepk6dtda4zerc53apy.us-east-1.es.amazonaws.com',
                                use_ssl=True, ca_certs=certifi.where())

    def delete_index(self, index_name):
        self.es.indices.delete(index_name)

    def create_index(self):
        request_body = \
            {
                'mappings':
                {
                    'commSentresults':
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
        self.es.indices.create(index='commsentresults', body=request_body)
        request_body = \
            {
                'mappings':
                {
                    'commReceivedresults':
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
        self.es.indices.create(index='commreceivedresults', body=request_body)
        request_body = \
            {
                'mappings':
                {
                    'cpuresults':
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
        self.es.indices.create(index='cpuresults', body=request_body)

    def upload_json_data(self, analysis_type, results_path):

        raw_configurations = self.config_file['configurations'][0].split('@')
        protocol_name = self.config_file['protocol']
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

    def upload_log_data(self, results_path):
        raw_configurations = self.config_file['configurations'][0].split('@')
        del raw_configurations[1::2]
        # raw_configurations = [rc[1:] for rc in raw_configurations]
        raw_configurations.insert(0, 'partyId')
        raw_configurations.insert(0, 'protocolName')

        dts = datetime.utcnow()
        results_files = glob('%s/*.log' % expanduser(results_path))
        protocol_name = self.config_file['protocol']
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



    def upload_all_data(self):
        is_external = json.loads(self.config_file['isExternal'].lower())
        results_path = self.config_file['resultsDirectory']
        if not is_external:
            self.upload_json_data('cpu', results_path)
        else:
            self.upload_log_data(results_path)

