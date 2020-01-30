import os
import datetime
import threading

import bson
import json
import botocore

from pymongo import errors
from pymongo import MongoClient
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from Deployment.deploy import DeployCP
from Deployment.aws_deploy import AmazonCP
from Execution.end_to_end import E2E
from Reporting.analyze_results import Analyze
from Reporting.upload_elastic import Elastic

# lock to serialize console output
lock = threading.Lock()

try:
    with open('GlobalConfigurations/tokens.json', 'r') as tokens:
        data = json.load(tokens)
        db_username = data['mongo']['user']
        db_password = data['mongo']['password']
        client = MongoClient(f'mongodb://{db_username}:{db_password}@127.0.0.1/BIU')
        db = client['BIU']
except EnvironmentError:
    print('Cannot open tokens file')


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bson.ObjectId) or isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


app = Flask(__name__)
CORS(app)


@app.route('/api/competitions/registerCompetition/<string:competition_name>', methods=['POST'])
def register_to_competition(competition_name):
    form = request.data
    form_data = json.loads(form.decode('utf-8'))
    protocol_name = form_data['protocolName']
    institute = form_data['institute']
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
    collection = db['competitions']
    competition = collection.find({'competitionName': competition_name}, {'_id': 0})
    for comp in competition:
        return jsonify(comp)

    return jsonify('Error retrieve competition')


@app.route('/api/competitions')
def get_competitions():
    collection = db['competitions']
    competitions_list = []

    for competition in collection.find({}, {'_id': 0}):
        # convert all competition values to string since datetime cannot be jsonify
        competition = dict((k, str(v)) for k, v in competition.items())
        competitions_list.append(competition)

    return json.dumps(competitions_list)


@app.route('/api/protocols')
def get_protocols():
    collection = db['protocols']
    protocols_list = []

    try:
        for protocols in collection.find({}, {'_id': 0}):
            # convert all protocols values to string since datetime cannot be jsonify
            protocols = dict((k, str(v)) for k, v in protocols.items())
            protocols_list.append(protocols)
    except errors.OperationFailure:
        return jsonify('reading failed', 500)

    return json.dumps(protocols_list)


@app.route('/api/protocols/<string:protocol_name>')
def get_protocol(protocol_name):
    collection = db['protocols']
    try:
        protocol = collection.find({'protocolName': protocol_name}, {'_id': 0})
    except errors.OperationFailure:
        return jsonify('reading failed', 500)
    return json.dumps(protocol[0])


@app.route('/api/protocols/createProtocol', methods=['POST'])
def register_new_protocol():
    form = request.data
    form_data = json.loads(form.decode('utf-8'))

    try:
        collection = db['protocols']
        collection.insert_one(form_data)
    except errors.OperationFailure:
        return jsonify('writing failed', 500)

    return jsonify('protocol registered')


@app.route('/api/protocols/update/<string:protocol_name>', methods=['POST'])
def update_protocol(protocol_name):
    form = request.data
    form_data = json.loads(form.decode('utf-8'))
    try:
        collection = db['protocols']
        doc = collection.find_one({'protocolName': protocol_name})
        doc['protocolName'] = form_data['protocolName']
        doc['institute'] = form_data['institute']
        doc['securityLevel'] = form_data['securityLevel']
        doc['thresholdLevel'] = form_data['thresholdLevel']
        doc['relatedArticle'] = form_data['relatedArticle']
        collection.save(doc)

    except errors.OperationFailure:
        return jsonify('writing failed', 500)

    return jsonify('protocol updated')


@app.route('/api/protocols/delete/<string:protocol_name>')
def delete_protocol(protocol_name):
    try:
        collection = db['protocols']
        collection.delete_one({'protocolName': protocol_name})

    except errors.OperationFailure:
        return jsonify('writing failed', 500)

    return jsonify('protocol deleted')


@app.route('/api/deployment/update/<string:protocol_name>', methods=['POST'])
def update_deployment_protocol_data(protocol_name):
    form = request.data
    form_data = json.loads(form.decode('utf-8'))
    try:
        collection = db['protocols']
        doc = collection.find_one({'protocolName': protocol_name})
        doc['cloudProviders'] = form_data['cloudProviders']
        collection.save(doc)

    except errors.InvalidDocument:
        return jsonify(f'Failed to retrieve data for {protocol_name}', 500)
    except errors.OperationFailure:
        return jsonify(f'Update deploy configuration for {protocol_name} failed', 500)

    return jsonify('deploy update works')


@app.route('/api/deployment/<string:protocol_name>/<string:operation>')
def execute_deployment_operation(protocol_name, operation):

    try:
        collection = db['protocols']
        doc = collection.find_one({'protocolName': protocol_name}, {'_id': 0})
        protocol_data = json.loads(json.dumps(doc))

        if 'AWS' in protocol_data['cloudProviders']:
            deploy = AmazonCP(protocol_data)
        else:
            deploy = DeployCP(protocol_data)

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

    except errors.InvalidDocument:
        return jsonify(f'Failed to retrieve data for {protocol_name}', 500)
    except errors.OperationFailure:
        return jsonify(f'Update deploy configuration for {protocol_name} failed', 500)
    except botocore.exceptions.ClientError as e:
        return jsonify(f'{str(e)}', 500)


@app.route('/api/execution/update/<string:protocol_name>', methods=['POST'])
def update_execution_protocol_data(protocol_name):
    form = request.data
    form_data = json.loads(form.decode('utf-8'))

    raw_configurations = form_data['configurations'].split(' ')
    numbers_of_configurations = int(form_data['numConfigurations'])
    numbers_of_parameters = len(raw_configurations) // numbers_of_configurations
    configurations = []

    for idx in range(numbers_of_configurations):
        configurations.append('@'.join(raw_configurations[idx * numbers_of_parameters:
                                                 (idx * numbers_of_parameters) + numbers_of_parameters]))

    form_data['configurations'] = configurations

    try:
        collection = db['protocols']
        doc = collection.find_one({'protocolName': protocol_name})
        doc['executableName'] = form_data['executableName'].strip()
        doc['configurations'] = form_data['configurations']
        doc['numConfigurations'] = form_data['numConfigurations']
        doc['numOfIterations'] = form_data['numOfIterations']
        doc['workingDirectory'] = form_data['workingDirectory'].strip()
        doc['resultsDirectory'] = form_data['resultsDirectory'].strip()
        collection.save(doc)

    except errors.InvalidDocument:
        return jsonify(f'Failed to retrieve data for {protocol_name}', 500)
    except errors.OperationFailure:
        return jsonify(f'Update deploy configuration for {protocol_name} failed', 500)

    return jsonify('execution update works')


@app.route('/api/execution/<string:protocol_name>/<string:operation>')
def execute_execution_operation(protocol_name, operation):
    try:
        collection = db['protocols']
        doc = collection.find_one({'protocolName': protocol_name}, {'_id': 0})
        protocol_data = json.loads(json.dumps(doc))

        ee = E2E(protocol_data)

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

    except errors.InvalidDocument:
        return jsonify(f'Failed to retrieve data for {protocol_name}', 500)
    except errors.OperationFailure:
        return jsonify(f'Update deploy configuration for {protocol_name} failed', 500)


@app.route('/api/reporting/<string:protocol_name>/<string:operation>')
def execute_reporting_operation(protocol_name, operation):
    try:
        collection = db['protocols']
        doc = collection.find_one({'protocolName': protocol_name}, {'_id': 0})
        protocol_data = json.loads(json.dumps(doc))
        reporting = Analyze(protocol_data)
        if operation == 'Download Results':
            reporting.download_data()
        elif operation == 'Analyze Results using Excel':
            reporting.download_data()
            reporting.analyze_results()
        elif operation == 'Analyze Results using Elasticsearch':
            e = Elastic(protocol_data)
            results_dir = doc['resultsDirectory']
            e.upload_json_data('cpu', results_dir)

        return jsonify('reporting operation %s succeeded' % operation)

    except errors.InvalidDocument:
        return jsonify(f'Failed to retrieve data for {protocol_name}', 500)
    except errors.OperationFailure:
        return jsonify(f'Update deploy configuration for {protocol_name} failed', 500)


@app.route('/api/deployment/getData/<string:protocol_name>')
def get_deployment_data(protocol_name):
    try:
        with open(f'WebApp/DeploymentLogs/{protocol_name}.log') as df:
            deployment_data = [line.rstrip('\n') for line in df.readlines()]
            return jsonify(str(deployment_data[:20]))
    except FileNotFoundError as e:
        print(str(e))
        return jsonify(f'file DeploymentLogs/{protocol_name}.log not created yet or operation failed')


@app.route('/api/execution/getData/<string:protocol_name>')
def get_execution_data(protocol_name):
    try:
        with open(f'WebApp/ExecutionLogs/{protocol_name}.log') as df:
            execution_data = [line.rstrip('\n') for line in df.readlines()]
            return jsonify(str(execution_data[-20:]))
    except FileNotFoundError as e:
        print(str(e))
        return jsonify(f'file ExecutionLogs/{protocol_name}.log not created yet or operation failed')


@app.route('/api/reporting/getData/<string:protocol_name>')
def get_reporting_data(protocol_name):
    try:
        with open(f'WebApp/ReportingLogs/{protocol_name}.log') as df:
            execution_data = [line.rstrip('\n') for line in df.readlines()]
            return jsonify(str(execution_data[-20:]))
    except FileNotFoundError as e:
        print(str(e))
        return jsonify(f'file ReportingLogs/{protocol_name}.log not created yet or operation failed')


@app.route('/api/deployment/downloadLog/<string:protocol_name>')
def get_deployment_log_file(protocol_name):
    return send_file(f'DeploymentLogs/{protocol_name}.log', attachment_filename=f'deployment_{protocol_name}.log')


@app.route('/api/execution/downloadLog/<string:protocol_name>')
def get_execution_log_file(protocol_name):
    return send_file(f'ExecutionLogs/{protocol_name}.log', attachment_filename=f'execution_{protocol_name}.log')


@app.route('/api/deployment/downloadConf/<string:protocol_name>')
def get_deployment_conf_file(protocol_name):
    try:
        collection = db['protocols']
        doc = collection.find_one({'protocolName': protocol_name}, {'_id': 0, 'cloudProviders': 1})
        return jsonify(doc)
    except errors.InvalidDocument:
        return jsonify(f'Failed to retrieve data for {protocol_name}', 500)
    except errors.OperationFailure:
        return jsonify(f'Update deploy configuration for {protocol_name} failed', 500)


@app.route('/api/execution/downloadConf/<string:protocol_name>')
def get_execution_conf_file(protocol_name):
    try:
        collection = db['protocols']
        doc = collection.find_one({'protocolName': protocol_name}, {'_id': 0, 'executableName': 1, 'configurations': 1,
                                                                    'numConfigurations': 1, 'numOfIterations': 1,
                                                                    'workingDirectory': 1, 'resultsDirectory': 1})
        return jsonify(doc)
    except errors.InvalidDocument:
        return jsonify(f'Failed to retrieve data for {protocol_name}', 500)
    except errors.OperationFailure:
        return jsonify(f'Update deploy configuration for {protocol_name} failed', 500)


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True, threaded=True)
