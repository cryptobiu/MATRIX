import datetime
import os
import urllib

import bson
import json

from pymongo import MongoClient
from flask import Flask, request, jsonify
from flask_cors import CORS

from Deployment.deploy import DeployCP
from Deployment.aws_deploy import AmazonCP
from Execution.end_to_end import E2E

with open('GlobalConfigurations/tokens.json', 'r') as tokens:
    data = json.load(tokens)
    db_username = data['mongo']['user']
    db_password = data['mongo']['password']


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bson.ObjectId) or isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


app = Flask(__name__)

# TODO: Restrict access from domains
CORS(app)


@app.route('/competitions')
def get_competitions():
    client = MongoClient('mongodb://%s:%s@127.0.0.1/BIU' % (db_username, db_password))
    db = client['BIU']
    collection = db['competitions']
    competitions_list = []

    for competition in collection.find({}, {'_id': 0}):
        # convert all competition values to string since datetime cannot be jsonify
        competition = dict((k, str(v)) for k, v in competition.items())
        competitions_list.append(competition)

    return json.dumps(competitions_list)


@app.route('/protocols')
def get_protocols():
    client = MongoClient('mongodb://%s:%s@127.0.0.1/BIU' % (db_username, db_password))
    db = client['BIU']
    collection = db['protocols']
    protocols_list = []

    for protocols in collection.find({}, {'_id': 0}):
        # convert all competition values to string since datetime cannot be jsonify
        protocols = dict((k, str(v)) for k, v in protocols.items())
        protocols_list.append(protocols)

    return json.dumps(protocols_list)


@app.route('/protocols/registerProtocol', methods=['POST'])
def register_new_protocol():
    form = request.data
    form_data = json.loads(form.decode('utf-8'))
    protocol_name = form_data['protocolName']
    address = form_data['repoAddress']
    security_level = form_data['securityLevel']
    security_threshold = form_data['thresholdLevel']
    client = MongoClient('mongodb://%s:%s@127.0.0.1/BIU' % (db_username, db_password))
    db = client['BIU']
    collection = db['protocols']
    protocol = {
        'name': protocol_name,
        'repoAddress': address,
        'securityLevel': security_level,
        'securityThreshold': security_threshold,
    }
    try:
        collection.insert_one(protocol)
    except bson.errors.InvalidDocument as e:
        return jsonify(e.with_traceback()), 500
    return jsonify('form submitted')


@app.route('/getprotocoldata/<string:protocol_name>')
def get_protocol_data(protocol_name):
    protocol_data = {}
    config_file = 'https://raw.githubusercontent.com/cryptobiu/MATRIX/web/ProtocolsConfigurations/Config_%s.json' \
                  % protocol_name
    raw_data = urllib.request.urlopen(config_file).read()
    data = json.loads(raw_data)
    raw_configurations = data['configurations']
    configurations = []

    for conf in raw_configurations:
        configurations.append(conf.replace('@', ' '))

    protocol_data['protocolName'] = data['protocol']
    protocol_data['numberOfParties'] = data['CloudProviders']['aws']['numOfParties']
    protocol_data['machineType'] = data['CloudProviders']['aws']['instanceType']
    protocol_data['regions'] = data['CloudProviders']['aws']['regions']
    protocol_data['configurations'] = configurations

    return jsonify(protocol_data)


@app.route('/deploy/<string:protocol_name>/<string:operation>')
def execute_deploy_operation(protocol_name, operation):

    config_file = 'https://raw.githubusercontent.com/cryptobiu/MATRIX/web/ProtocolsConfigurations/Config_%s.json' \
                  % protocol_name
    raw_data = urllib.request.urlopen(config_file).read()
    data = json.loads(raw_data)

    if 'aws' in data['CloudProviders']:
        deploy = AmazonCP(data)
    else:
        deploy = DeployCP(data)

    if operation == 'Deploy Instance(s)':
        deploy.deploy_instances()
    elif operation == 'Create key pair(s)':
        deploy.create_key_pair()
    elif operation == 'Create security group':
        deploy.create_security_group()
    elif operation == 'Update network details':
        deploy.get_network_details()
    elif operation == 'Terminate machines':
        deploy.terminate_instances()
    elif operation == 'Change machines types':
        deploy.change_instance_types()
    elif operation == 'Start instances':
        deploy.start_instances()
    elif operation == 'Stop instances':
        deploy.stop_instances()

    return jsonify('deployment operation %s succeeded' % operation)


@app.route('/execute/<string:protocol_name>/<string:operation>')
def execute_execution_operation(protocol_name, operation):
    config_file = 'https://raw.githubusercontent.com/cryptobiu/MATRIX/web/ProtocolsConfigurations/Config_%s.json' \
                  % protocol_name
    raw_data = urllib.request.urlopen(config_file).read()
    data = json.loads(raw_data)

    config_file_path = '%s/%s.json' % (os.getcwd(), protocol_name)

    ee = E2E(data, config_file_path)

    with open(config_file_path, 'w+') as fp:
        json.dump(data, fp)

    if operation == 'Install Experiment':
        ee.install_experiment()
    elif operation == 'Execute Experiment':
        ee.execute_experiment()
    elif operation == 'Execute Experiment with profiler':
        ee.execute_experiment_callgrind()
    elif operation == 'Update libscapi':
        ee.update_libscapi()

    return jsonify('execution operation %s succeeded' % operation)


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True)
