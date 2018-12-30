import datetime

import bson
import json

from pymongo import MongoClient
from flask import Flask, request, jsonify
from flask_cors import CORS

with open('../GlobalConfigurations/tokens.json', 'r') as tokens:
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


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True)
