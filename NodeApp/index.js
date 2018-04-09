console.log('server is starting');

var express = require('express');
var session = require('express-session');
var app = express();
var index = require('./routes/index');
var polls = require('./routes/polls');
var path = require('path');

app.use(session({ resave: true ,secret: 'MATRIX' , saveUninitialized: true}));
app.use('/', index);
app.use('/polls', polls);
app.use(express.static('public'));

// view engine setup
app.engine('pug', require('pug').__express)
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(function(err, req, res) {
  console.error(err.stack);
  res.statusCode(500).send('Something broke!');
});

app.listen(8080, function () {
    console.log('App listening on port 8080!');
});
