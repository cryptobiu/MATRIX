console.log('server is starting')

const express = require('express');
const app = express();
const index = require('./routes/index');
const polls = require('./routes/polls')
const path = require('path');

app.use('/', index)
app.use('/polls', polls)
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
