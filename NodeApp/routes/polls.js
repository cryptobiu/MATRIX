const express = require('express');
const router = express.Router();
const polls_controller = require('./../controllers/pollsControllers');

router.get('/', function (req, res) {
    res.render('polls', { title: 'Polls' });
});

router.get('/prepareOnline', function (req, res) {
    res.render('prepareOnline', { title: 'Prepare for Online' })
    // polls_controller.prepareOnline(req, res);
});

router.post('/prepareOnline', function (req, res) {
    polls_controller.prepareOnline(req, res);
});

router.get('/parties', function (req, res) {
    res.download('public/assets/parties.conf')
});

router.get('/circuit', function (req, res) {
    res.download('public/assets/1000000G_1000000MG_200In_50Out_20D_OutputOne5P.txt')
});

router.get('/configuration', function (req, res) {
    res.download('public/assets/Config_SecretSharing.json')
});

router.get('/isReadyForPoll', function (req, res) {
    // polls_controller.isReadyForPoll(req, res);
    res.render('isReadyForPoll', { title: 'Poll ready?' })
});

router.get('/executePoll', function (req, res) {
    res.render('executePoll', { title: 'Poll execution' })
});

router.get('/isPollFinished', function (req, res) {
    res.render('isReadyForPoll', { title: 'Poll Status for Execution' })
});


router.get('/mapping', function (req, res) {
    res.download('public/assets/mapping.json')
});

module.exports = router;

