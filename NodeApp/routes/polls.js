const express = require('express');
const router = express.Router();

const pythonShell = require('python-shell');
const spawn = require('child_process').spawn;

router.get('/', function (req, res) {
    res.render('polls', { title: 'Polls' });
});

router.get('/parties', function (req, res) {
    res.download('public/assets/parties.conf')
});

router.get('/configuration', function (req, res) {
    res.download('public/assets/Config_SecretSharing.json')
});

router.get('/circuit', function (req, res) {
    res.download('public/assets/1000000G_1000000MG_200In_50Out_20D_OutputOne5P.txt')
});

router.get('/mapping', function (req, res) {
    res.download('public/assets/mapping.json')
});

module.exports = router;

