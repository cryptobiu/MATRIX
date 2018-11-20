import datetime
from functools import wraps

import bson

from pymongo import MongoClient
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_login import LoginManager

from FlaskApp.competition_forms import CompetitionForm, CompetitionRegistrationForm

login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html', title='-About')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form
        session['user'] = user
        session['logged_in'] = True
        return url_for('index')
    if request.method == 'GET':
        return render_template('login.html', title='-Login')


@app.route('/circuits')
def circuits():
    return render_template('circuits.html', title='-Circuits')


@app.route('/competitions')
@is_logged_in
def competitions():
    client = MongoClient()
    db = client['BIU']
    collection = db['Competitions']
    competitions_list = []

    for competition in collection.find({}):
        competitions_list.append(competition)

    return render_template('competitions.html', title='-Competitions', competitions=competitions_list)


@app.route('/competitions_manage', methods=['GET', 'POST'])
def competitions_management():
    form = CompetitionForm(request.form)
    if request.method == 'POST':
        name = form.name.data
        description = form.description.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        status = form.status.data
        start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
        end_date = datetime.datetime.combine(end_date, datetime.datetime.min.time())

        client = MongoClient()
        db = client['BIU']
        collection = db['Competitions']
        competition = {
            'competitionName': name,
            'description': description,
            'startDate': start_date,
            'endDate': end_date,
            'status': status
        }

        try:
            competition_id = collection.insert_one(competition)
            if competition_id.acknowledged:
                flash('Competition added', 'success')
        except bson.errors.InvalidDocument:
            flash('Failed to create new competition', 'danger')

        return redirect(url_for('competitions'))

    return render_template('competitions_manage.html', title='-CompetitionsAdminPanel', form=form)


@app.route('/register_competition/<string:competition_name>', methods=['GET', 'POST'])
def register_competition(competition_name):
    form = CompetitionRegistrationForm(request.form)
    if request.method == 'POST':
        return redirect(url_for('competitions'))

    return render_template('register_competition.html', title='-%s Registration' % competition_name, form=form)


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True)
