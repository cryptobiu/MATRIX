var express = require('express');
var app = express();
var experiments = require('./routes/experiments');
var reports = require('./routes/reports');
var index = require('./routes/index');
var path = require('path');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var expressValidator = require('express-validator');

app.use('/', index);
app.use('/experiments', experiments);
app.use('/reports', reports);
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(expressValidator());
app.use(express.static('public'));

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(function(err, req, res, next) {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

app.listen(4000, function () {
    console.log('Example app listening on port 4000!');
})