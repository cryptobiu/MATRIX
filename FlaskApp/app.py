import datetime
from functools import wraps

import bson
import json

from pymongo import MongoClient
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
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


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


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


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True)
