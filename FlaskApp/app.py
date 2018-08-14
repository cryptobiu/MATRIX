from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from collections import OrderedDict
from pymongo import MongoClient
from functools import wraps

import os
import wget
import json
from bson.json_util import dumps, loads

from InstancesManagement import aws_deploy

app = Flask(__name__)


# Config MySQL

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'matrix'
app.config['MYSQL_PASSWORD'] = 'matrixroot'
app.config['MYSQL_DB'] = 'MATRIX'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=4, max=50)])
    username = StringField('Username', [validators.length(min=4, max=50)])
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match'),
        validators.length(min=6, max=50)
    ])
    confirm = PasswordField('Confirm Password', [validators.length(min=6, max=50)])


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        name = form.name.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        cur.execute('INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)',
                    (name, email, username, password))

        mysql.connection.commit()

        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_cand = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # get user by user name
        result = cur.execute('SELECT * FROM users WHERE username = %s', [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # compare passwords
            if sha256_crypt.verify(password_cand, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))

            else:
                error = 'invalid login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash(' You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
    config_files = []
    client = MongoClient()
    db = client['Experiments']
    collection = db['Configurations']

    for doc in collection.find({}):
        config_files.append(doc['protocol'])

    if len(config_files) > 0:
        return render_template('dashboard.html', config_files=config_files)
    else:
        msg = 'No config files found'
        return render_template('dashboard.html', msg=msg)


# Config files class
class ConfigFileForm(Form):
    title = StringField('Title', [validators.length(min=5)])
    body = TextAreaField('Body', [validators.length(min=10)])


class ConfigFileRegistration(Form):
    protocol_name = StringField('Name', [validators.length(min=5)])
    address = StringField('Address', [validators.URL()])


@app.route('/add_config', methods=['GET', 'POST'])
@is_logged_in
def add_config_file():
    form = ConfigFileRegistration(request.form)
    if request.method == 'POST' and form.validate():
        address = form.address.data
        address = address.replace('github.com', 'raw.githubusercontent.com')
        address = address.replace('blob/', '')
        file = wget.download(address, out='%s/Uploads' % os.getcwd())

        client = MongoClient()
        db = client['Experiments']
        collection = db['Configurations']

        with open(file) as fd:
            data = json.load(fd, object_pairs_hook=OrderedDict)

        config_id = collection.insert_one(data)

        if config_id.acknowledged:
            flash('Config file added', 'success')
        else:
            flash('Failed to add configuration', 'danger')

        return redirect(url_for('dashboard'))

    return render_template('add_config.html', form=form)


@app.route('/edit_config/<string:title>', methods=['GET', 'POST'])
@is_logged_in
def edit_config_file(title):

    form = ConfigFileForm(request.form)
    client = MongoClient()
    db = client['Experiments']
    collection = db['Configurations']

    result = collection.find({'protocol': title}).next()

    form.title.data = title
    form.body.data = result
    if request.method == 'POST' and form.validate():
        try:
            json_data = dumps(form.body.data)
            d = loads(json_data)
            for key in d.keys():
                res_update = collection.update_one({'protocol': form.title.data},
                                                   {'$set': {key: d[key]}})
            if res_update.modified_count == 0:
                flash('%s updated successfully' % title, 'success')
        except ValueError:
            flash('Error while updating: The inserted data was not a valid json file', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('edit_config.html', form=form, title=title)


@app.route('/delete_file/<string:title>', methods=['POST'])
@is_logged_in
def delete_file(title):
    client = MongoClient()
    db = client['Experiments']
    collection = db['Configurations']

    collection.delete_one({'protocol': title})

    flash('Config file %s deleted' % title, 'success')

    return redirect(url_for('dashboard'))


@app.route('/deploy_experiment/<string:title>', methods=['GET', 'POST'])
@is_logged_in
def deploy_experiment(title):

    client = MongoClient()
    db = client['Experiments']
    collection = db['Configurations']
    result = collection.find({'protocol': title}).next()
    regions = list(result['regions'].values())
    number_of_parties = max(list(result['numOfParties'].values()))

    if request.method == 'POST':
        json_data = dumps(result)
        d = loads(json_data)
        del d['_id']
        deploy = aws_deploy.AmazonCP(d)
        deploy.deploy_instances()

        return redirect(url_for('dashboard'))

    return render_template('deploy_config.html', title=title, regions=regions, number_of_parties=number_of_parties)


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True)
