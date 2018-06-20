const express = require('express');
const router = express.Router();
const pollscontrollerNew = require('./../controllers/pollsControllerNew');

router.get('/', function (req, res) {
    res.render('polls', { title: 'Polls' });
});

router.get('/openForRegistration/:pollName', function (req, res) {
    pollscontrollerNew.openForRegistration(req, res);
});

router.get('/registerToPoll/:pollName/:ip/:type', function (req, res) {
    pollscontrollerNew.registerToPoll(req, res);
});

router.get('/getPollParams/:ip', function (req, res) {
    pollscontrollerNew.getPollsParams(req, res);
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
    res.download('NodeApp/public/assets/parties.conf')
});

router.get('/circuit', function (req, res) {

    var numberOfOnline = req.session.NumberOfOnlineParties;
    var numberOfOffline = req.session.NumberOfOfflineParties;
    var numberOfParties = parseInt(numberOfOnline) + parseInt(numberOfOffline);
    var inputs = Math.floor(1000 / numberOfParties);
    var fileName = '';
    if (isNaN(numberOfParties) || isNaN(inputs))
        fileName = '1000G_1000MG_333In_50Out_10D_OutputOne3P.txt' ;
    else
        fileName = '1000G_1000MG_' + inputs.toString() + 'In_50Out_20D_OutputOne' +
            numberOfParties.toString() + 'P.txt';
    res.download('NodeApp/public/assets/'+ fileName);
});

router.get('/configuration', function (req, res) {
    res.download('NodeApp/public/assets/Config_SecretSharing.json')
});

router.get('/mapping', function (req, res) {
    res.download('public/assets/mapping.json')
});

module.exports = router;

