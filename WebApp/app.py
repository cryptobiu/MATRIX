import datetime
import os
import requests

import bson
import json

from pymongo import MongoClient
from flask import Flask, request, jsonify
from flask_cors import CORS

from Deployment.deploy import DeployCP
from Deployment.aws_deploy import AmazonCP
from Execution.end_to_end import E2E
from Reporting.analyze_results import Analyze
from Reporting.upload_elastic import Elastic

try:
    with open('GlobalConfigurations/tokens.json', 'r') as tokens:
        data = json.load(tokens)
        db_username = data['mongo']['user']
        db_password = data['mongo']['password']
except EnvironmentError:
    print('Cannot open tokens file')


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bson.ObjectId) or isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


app = Flask(__name__)
CORS(app)


@app.route('/api/competitions')
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


@app.route('/api/protocols')
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


@app.route('/api/protocols/registerProtocol', methods=['POST'])
def register_new_protocol():
    form = request.data
    form_data = json.loads(form.decode('utf-8'))
    protocol_name = form_data['protocolName']
    raw_configurations = form_data['configurations'].split(' ')

    conf_dict = {}
    for idx in range(0, len(raw_configurations), 2):
        key = raw_configurations[idx]
        value = raw_configurations[idx + 1]
        if key not in conf_dict.keys():
            conf_dict[key] = []
        conf_dict[key].append(value)

    # get the length of the values by retrieve the last key
    numbers_of_configurations = len(conf_dict[raw_configurations[-2]])
    configurations = []

    for idx in range(numbers_of_configurations):
        configuration = ''
        for key, value in conf_dict.items():
            configuration += f'{key}@{value[idx]}@'
        configurations.append(configuration)

    form_data['configurations'] = configurations
    with open(f'{os.getcwd()}/{protocol_name}.json', 'w+') as fp:
        json.dump(form_data, fp)
    return jsonify('form submitted')


@app.route('/api/competitions/registerCompetition/<string:competition_name>', methods=['POST'])
def register_to_competition(competition_name):
    form = request.data
    form_data = json.loads(form.decode('utf-8'))
    protocol_name = form_data['protocolName']
    institute = form_data['institute']
    client = MongoClient('mongodb://%s:%s@127.0.0.1/BIU' % (db_username, db_password))
    db = client['BIU']
    collection = db['competitions']
    competition = collection.find({'competitionName': competition_name}, {'participants': []})
    try:
        for comp in competition:
            if len(comp.keys()) == 1:
                participants = []
            else:
                participants = comp['participants']
            participants.append({'protocolName': protocol_name, 'institute': institute})
        collection.update({'competitionName': competition_name}, {'$set': {'participants': participants}})
    except bson.errors.InvalidDocument as e:
        return jsonify(e.with_traceback()), 500
    return jsonify('form submitted')


@app.route('/api/competitions/<string:competition_name>')
def get_competition_data(competition_name):
    client = MongoClient('mongodb://%s:%s@127.0.0.1/BIU' % (db_username, db_password))
    db = client['BIU']
    collection = db['competitions']
    competition = collection.find({'competitionName': competition_name}, {'_id': 0})
    for comp in competition:
        return jsonify(comp)

    return jsonify('Error retrieve competition')


@app.route('/api/deploy/<string:protocol_name>/<string:operation>')
def execute_deploy_operation(protocol_name, operation):

    config_file = 'https://raw.githubusercontent.com/cryptobiu/MATRIX/master/ProtocolsConfigurations/Config_%s.json' \
                  % protocol_name
    raw_data = requests.get(config_file)
    try:
        raw_data.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print('Error while fetching configuration file: %s' % e.response.reason)
        return jsonify('Error!!!')

    data = json.loads(raw_data.content)

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


@app.route('/api/execute/<string:protocol_name>/<string:operation>')
def execute_execution_operation(protocol_name, operation):
    config_file = 'https://raw.githubusercontent.com/cryptobiu/MATRIX/master/ProtocolsConfigurations/Config_%s.json' \
                  % protocol_name
    raw_data = requests.get(config_file)
    try:
        raw_data.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print('Error while fetching configuration file: %s' % e.response.reason)
        return jsonify('Error!!!')
    data = json.loads(raw_data.content)

    config_file_path = '%s/%s.json' % (os.getcwd(), protocol_name)

    try:
        with open(config_file_path, 'w') as fp:
            json.dump(data, fp)
    except EnvironmentError:
        print(f'Cannot write {config_file_path}')
        return

    ee = E2E(data, config_file_path)

    if operation == 'Install Experiment':
        ee.install_experiment()
    elif operation == 'Execute Experiment':
        ee.execute_experiment()
    elif operation == 'Execute Experiment with profiler':
        ee.execute_experiment_callgrind()
    elif operation == 'Get Logs':
        ee.get_logs()
    elif operation == 'Update libscapi':
        ee.update_libscapi()

    return jsonify('execution operation %s succeeded' % operation)


@app.route('/api/reporting/<string:protocol_name>/<string:operation>')
def execute_reporting_operation(protocol_name, operation):
    config_file = 'https://raw.githubusercontent.com/cryptobiu/MATRIX/master/ProtocolsConfigurations/Config_%s.json' \
                  % protocol_name
    raw_data = requests.get(config_file)
    try:
        raw_data.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print('Error while fetching configuration file: %s' % e.response.reason)
        return jsonify('Error!!!')

    data = json.loads(raw_data.content)

    if operation == 'Analyze Results using Excel':
        reporting = Analyze(data)
        reporting.download_data()
        reporting.analyze_results()
    elif operation == 'Analyze Results using Elasticsearch':
        e = Elastic(data)
        e.upload_all_data()

    return jsonify('reporting operation %s succeeded' % operation)


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True)
