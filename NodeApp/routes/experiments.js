const express = require('express');
const router = express.Router();
const experiment_controller = require('./../controllers/experimentController');
const pythonShell = require('python-shell');
const spawn = require('child_process').spawn;

var uint8arrayToString = function(data){
    return String.fromCharCode.apply(null, data);
};


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

    const scriptExec = spawn('python3', ['ImagesDeployment/deploy_machines.py',
        'Configurations/Config_MPCHonestMajorityNoTriples.json']);

    scriptExec.stdout.on('data', (data) =>
        {
            console.log(uint8arrayToString(data));
        });

    // var process = exec('python3', ['../ImagesDeployment/deploy_machines.py', '../Config_MPCHonestMajorityNoTriples.json']);
    // process.stdout.on('data', function (data) {
    //     console.log(data);
    // });
    // process.stderr.on('data', function (data) {
    //     console.log(data);
    // });
    // var options =
    //     {
    //         mode: 'text',
    //         pythonPath:'/usr/bin/python3.5',
    //         pythonOptions: ['-u'],
    //         scriptPath: 'ImagesDeployment/',
    //         args: ['Configurations/Config_GMW.json']
    //     };
    // pythonShell.run('deploy_machines.py', options, function (err, pythonRes) {
    //     if(err) throw err;
    //
    //     console.log('results: %j', pythonRes);
    //     res.render('experiment_execute', { output: pythonRes });
    // })
    //
    // var options2 =
    //     {
    //         mode: 'text',
    //         pythonPath:'/usr/bin/python3.5',
    //         pythonOptions: ['-u'],
    //         scriptPath: 'ExperimentExecute/',
    //         args: ['Configurations/Config_GMW.json']
    //     };
    //
    // pythonShell.run('end_to_end.py', options2, function (err, pythonRes) {
    //     if(err) throw err;
    //
    //     console.log('results: %j', pythonRes);
    //     res.render('experiment_execute', { output: pythonRes });
    // })

    // const { stdout, stderr } = exec('python3');
    // console.log('stdout:', stdout);
    // console.log('stderr:', stderr);
});



module.exports = router;