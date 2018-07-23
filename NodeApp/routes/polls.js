const express = require('express');
const router = express.Router();
const pollscontroller = require('../controllers/pollsController');

router.get('/', function (req, res) {
    res.render('polls', { title: 'Polls' });
});

router.get('/openForRegistration/:pollName', function (req, res) {
    pollscontroller.openForRegistration(req, res);
});

router.get('/registerToPoll/:pollName/:ip/:type', function (req, res) {
    pollscontroller.registerToPoll(req, res);
});

router.get('/getPollParams/:pollName/:ip', function (req, res) {
    let ip = req.params.ip;
    res.download('public/assets/' + ip + '.json')
});

router.get('/changePollState/:state', function (req, res) {
    pollscontroller.changePollState(req, res);
});

router.get('/closePollForRegistration/:pollName', function (req, res) {
    pollscontroller.closePollForRegistration(req, res);
});

router.get('/runProxyClients', function (req, res) {
    pollscontroller.runProxyClients(req, res);
});

/*
* Download files zone
*/

router.get('/parties', function (req, res) {
    res.download('public/assets/parties.conf')
});

router.get('/circuit/:circuitName', function (req, res) {

    let circuitName = req.params.circuitName;
    res.download('public/assets/' + circuitName);
});

router.get('/configuration', function (req, res) {
    res.download('NodeApp/public/assets/Config_SecretSharing.json')
});

router.get('/mapping', function (req, res) {
    res.download('public/assets/mapping.json')
});

module.exports = router;

