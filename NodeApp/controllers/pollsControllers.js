var formidable = require('formidable');
var spawn = require('child_process').spawn;
var PythonShell = require('python-shell');
var options = {
    mode:'text',
    pythonPath: '/usr/bin/python3.5',
    pythonOptions:['-u']
};


exports.prepareOnline = function (req, res) {
    var form = new formidable.IncomingForm();
    form.multiples = true;
    form.keepExtensions = true;

    form.parse(req, function(err, fields) {
        var pollName =  fields['name'];
        var numberOfOnlineParties =  fields['numberOfOnlineParties'];
        var numberOfOfflineParties =  fields['numberOfOfflineParties'];
        var arr = fields['IPs'].split(",");

        // init python shell
        var pyshell = new PythonShell('../main.py', options);
        // enter to Deploy instances menu
        pyshell.send('1');
        // insert the configuration file
        pyshell.send('../NodeApp/public/assets/Config_SecretSharing.json');
        // invoke get_aws_network_details_from_api
        pyshell.send('6');
        // send to python shell the online users ips
        pyshell.send(fields['IPs']);
        // entr to execution menu
        pyshell.send('2');
        // insert the configuration file
        pyshell.send('../NodeApp/public/assets/Config_SecretSharing.json');
        //install experiment at aws machines
        pyshell.send('1');
        // exit python shell
        pyshell.send('4');

        pyshell.end(function (err, code, signal) {
            if(err) throw err;
            console.log('The exit code was: ' + code);
            console.log('The exit signal was: ' + signal);
            console.log('finished');
            console.log('finished');
        });
        res.redirect('/polls');
    });
};

exports.isReadyForPoll = function (req, res) {
    // var timer = ms => new Promise( r => setTimeout(r, 2000));
    res.redirect('/polls');
};

exports.executePoll = function (req, res) {
    // init python shell
        var pyshell = new PythonShell('../main.py', options);
        // enter to Deploy instances menu
        pyshell.send('2');
        // insert the configuration file
        pyshell.send('../NodeApp/public/assets/Config_SecretSharing.json');
        // invoke get_aws_network_details_from_api
        pyshell.send('3');
        // exit python shell
        pyshell.send('4');
};

exports.isPollFinished = function (req, res) {
    spawn('python3', []);
};