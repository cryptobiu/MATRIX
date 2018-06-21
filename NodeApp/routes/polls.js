const express = require('express');
const router = express.Router();
const pollscontrollerNew = require('./../controllers/pollsControllerNew');
const fs = require('fs');

router.get('/', function (req, res) {
    res.render('polls', { title: 'Polls' });
});

router.get('/openForRegistration/:pollName', function (req, res) {
    pollscontrollerNew.openForRegistration(req, res);
});

router.get('/registerToPoll/:pollName/:ip/:type', function (req, res) {
    pollscontrollerNew.registerToPoll(req, res);
});

router.get('/getPollParams/:pollName/:ip', function (req, res) {
    let ip = req.params.ip;
    res.download('public/assets/' + ip + '.json')
});

router.get('/changePollState/:state', function (req, res) {
    pollscontrollerNew.changePollState(req, res);
});

router.get('/closePollForRegistration/:pollName', function (req, res) {
    pollscontrollerNew.closePollForRegistration(req, res);
});

/*
* Download files zone
*/

router.get('/parties', function (req, res) {
    res.download('public/assets/parties.conf')
});

router.get('/circuit/:circuitName', function (req, res) {

    let circuitName = req.params.circuitName;
    fs.readFile('public/assets/'+circuitName, 'utf8', function (error, data) {
    if (error) throw error;
    res.write(data.toString());
});
});

router.get('/configuration', function (req, res) {
    res.download('NodeApp/public/assets/Config_SecretSharing.json')
});

router.get('/mapping', function (req, res) {
    res.download('public/assets/mapping.json')
});

module.exports = router;

