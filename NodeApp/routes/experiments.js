var express = require('express');
var router = express.Router();
var experiment_controller = require('./../controllers/experimentController');


//Experiments page route
router.get('/', function (req, res) {
    res.render('experiments');
});

router.get('/create', function (req, res) {
 experiment_controller.experiment_create_get(req, res);
});

router.post('/create', function (req, res) {
 experiment_controller.experiment_create_post(req, res);
});

router.get('/experiment_execute', function (req, res) {
    res.render('experiment_execute');
});



module.exports = router;