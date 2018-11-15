import datetime
import bson
import oauth2

from pymongo import MongoClient
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager

from FlaskApp.competition_form import CompetitionForm

login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html', title='-About')


@app.route('/login', methods=['GET', 'POST'])
def login():
    consumer = oauth2.Consumer(key='ConsumeKey', secret='SecretKey')
    token = oauth2.Token(key='key', secret='secret')
    client = oauth2.Client(consumer, token)
    resp, content = client.request('url', method='http_method', body='')
    return render_template('login.html')


@app.route('/circuits')
def circuits():
    return render_template('circuits.html', title='-Circuits')


@app.route('/competitions')
def competitions():
    client = MongoClient()
    db = client['BIU']
    collection = db['Competitions']
    competitions_list = []

    for competition in collection.find({}):
        competitions.append(competition)

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


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True)
