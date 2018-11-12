from flask import Flask, render_template


app = Flask(__name__)
config = {
    'apiKey': "AIzaSyB0PQ0E_BuVBE2X6r-hXk88KLvi4ZwiRjc",
    'authDomain': "matrixwebui.firebaseapp.com",
    'databaseURL': "https://matrixwebui.firebaseio.com",
    'projectId': "matrixwebui",
    'storageBucket': "matrixwebui.appspot.com",
    'messagingSenderId': "547583715969"
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True)
