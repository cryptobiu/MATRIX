var express = require('express');
var router = express.Router();

//Reports page route
router.get('/', function (req, res) {
    res.render('reports')
});

module.exports = router;