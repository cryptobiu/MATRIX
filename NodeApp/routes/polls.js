var express = require('express');
var router = express.Router();
var polls_controller = require('./../controllers/pollsControllers');

router.get('/', function (req, res) {
    res.render('polls', { title: 'Polls' });
});

router.get('/prepareOnline', function (req, res) {
    res.render('prepareOnline', { title: 'Prepare for Online' })
    // polls_controller.prepareOnline(req, res);
});

router.get('/prepareOnline/:ip', function (req, res) {
    // res.render('prepareOnline', { title: 'Prepare for Online' })
    polls_controller.saveIpAddress(req, res);
});

router.post('/prepareOnline', function (req, res) {
    polls_controller.prepareOnline(req, res);
});

router.get('/parties', function (req, res) {
    res.download('public/assets/parties.conf')
});

router.get('/circuit', function (req, res) {
    //var numberOfOnline = req.session.NumberOfOnlineParties;
    //var numberOfOffline = req.session.NumberOfOfflineParties;
    //var numberOfParties = parseInt(numberOfOnline) + parseInt(numberOfOffline);
    //var inputs = Math.floor(1000 / numberOfParties);
    var fileName = '1000G_1000MG_333In_50Out_10D_OutputOne3P.txt' ;
    res.download('public/assets/'+ fileName);
});

router.get('/configuration', function (req, res) {
    res.download('public/assets/Config_SecretSharing.json')
});

router.get('/isReadyForPoll', function (req, res) {
    // res.locals pass data to the pug view
    res.locals.isReadyForPoll = polls_controller.isReadyForPollLoop(req, res);
    res.render('isReadyForPoll', { title: 'Poll ready?' })
});

router.get('/preExecutePoll', function (req, res) {
    res.locals.executePoll = polls_controller.executePoll(req, res);
    res.render('preExecutePoll', { title: 'Poll execution' })
});

router.get('/executePoll', function (req, res) {
    res.render('executePoll', { title: 'Poll execution' })
});

router.get('/isPollFinished', function (req, res) {
    res.render('isPollFinished', { title: 'Poll Status for Execution' })
});


router.get('/mapping', function (req, res) {
    res.download('public/assets/mapping.json')
});

module.exports = router;

