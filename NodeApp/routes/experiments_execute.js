var express = require('express');
var router = express.Router();


//Experiments page route
router.get('/', function (req, res) {
    res.render('experiment_execute');
});



module.exports = router;