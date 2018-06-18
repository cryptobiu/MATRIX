const express = require('express');
const router = express.Router();
const polls_controller = require('./../controllers/pollsControllers');
const pollscontrollerNew = require('./../controllers/pollsControllerNew');

router.get('/', function (req, res) {
    res.render('polls', { title: 'Polls' });
});

router.get('/openForRegistration/:pollName', function (req, res) {
    pollscontrollerNew.openForRegistration(req, res);
});

router.get('/registerToPoll/:ip/:type', function (req, res) {
    pollscontrollerNew.registerToPoll(req, res);
});

router.get('/getPollParams/:ip', function (req, res) {
    pollscontrollerNew.getPollsParams(req, res);
});

router.get('/changePollState/:state', function (req, res) {
    pollscontrollerNew.changePollState(req, res);
});

/*
* Prepare online section - including API calls
*/

router.get('/prepareOnline', function (req, res) {
    res.render('prepareOnline', { title: 'Prepare for Online' })
});

router.get('/prepareOnlineAPI', function (req, res) {
    polls_controller.prepareOnlineAPI(req, res);
});

router.get('/prepareOnline/:ip', function (req, res) {
    polls_controller.saveIpAddress(req, res);
});

router.post('/prepareOnline', function (req, res) {
    polls_controller.prepareOnline(req, res);
});

/*
* Execute poll section - including API calls
*/

router.get('/executePoll', function (req, res) {
    res.render('executePoll', { title: 'Poll execution' })
});

router.get('/executePollAPI', function (req, res) {
    polls_controller.executePollAPI(req, res);
});

router.get('/isReadyForPoll', function (req, res) {
    // res.locals pass data to the pug view
    res.locals.isReadyForPoll = polls_controller.isReadyForPollLoop(req, res);
    res.render('isReadyForPoll', { title: 'Poll ready?' })
});

router.get('/isPollCompleted', function (req, res) {
    polls_controller.isPollCompleted(req, res);
});


/*
* Download files zone
*/

router.get('/parties', function (req, res) {
    res.download('NodeApp/public/assets/parties.conf')
});

router.get('/getMyId/:ip', function (req, res) {
    polls_controller.getMyId(req, res);
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

