const formidable = require('formidable');
const PythonShell = require('python-shell');
const url = require('url');
const sleep = require('sleep');
const fs = require('fs');
const redis = require('redis');
const options = {
    mode:'text',
    pythonPath: '/usr/bin/python3.5',
    pythonOptions:['-u']
};


// exports.prepareOnline = function (req, res) {
//     var form = new formidable.IncomingForm();
//     form.multiples = true;
//     form.keepExtensions = true;
//
//     form.parse(req, function(err, fields) {
//         var pollName =  fields['name'];
//         var numberOfOnlineParties =  fields['numberOfOnlineParties'];
//         var numberOfOfflineParties =  fields['numberOfOfflineParties'];
//         var ips = fields['IPs'];
//         req.session.PollName = pollName;
//         req.session.NumberOfOnlineParties = numberOfOnlineParties;
//         req.session.NumberOfOfflineParties = numberOfOfflineParties;
//
//         // init python shell
//         var pyshell = new PythonShell('main.py', options);
//
//         if (numberOfOfflineParties > 0)
//         {
//             // enter to Deploy instances menu
//             pyshell.send('1')
//             // insert the configuration file
//             pyshell.send('NodeApp/public/assets/Config_SecretSharing.json');
//             // deploy instances
//             pyshell.send('1');
//         }
//
//         // insert the configuration file
//         pyshell.send('NodeApp/public/assets/Config_SecretSharing.json');
//         // invoke get_aws_network_details_from_api
//         pyshell.send('6');
//         // send to python shell the online users ips
//         pyshell.send(ips);
//         // enter to execution menu
//         pyshell.send('4');
//
//         pyshell.end(function (err, code, signal) {
//             if(err) throw err;
//             console.log('The exit code was: ' + code);
//             console.log('The exit signal was: ' + signal);
//             console.log('finished');
//         });
//         res.redirect('/polls');
//     });
// };

exports.prepareOnlineAPI = function (req, res) {
    var queryData = url.parse(req.url, true).query;
    var numberOfOnline = queryData.nonline;
    var numberOfOffline = queryData.noffline;

    req.session.NumberOfOnlineParties = numberOfOnline;
    req.session.NumberOfOfflineParties = numberOfOffline;
    if(!isNaN(numberOfOffline) && numberOfOffline > 0)
    {
        var pyshell = new PythonShell('main.py', options);
        // enter to Deploy instances menu
        pyshell.send('1');
        // enter configuration file
        pyshell.send('NodeApp/public/assets/Config_SecretSharing.json');
        // send deploy instances command
        pyshell.send('1');
        sleep.msleep(240000)

        // enter to execute menu
        pyshell.send('2');
        // enter configuration file
        pyshell.send('NodeApp/public/assets/Config_SecretSharing.json');
        // update libscapi
        pyshell.send('4');
        pyshell.send('dev')
        // enter configuration file
        pyshell.send('NodeApp/public/assets/Config_SecretSharing.json');
        // install experiment on the offline parties
        pyshell.send('1');
        //exit
        pyshell.send('4');

        pyshell.end(function (err, code, signal) {
            if(err) throw err;
            console.log('The exit code was: ' + code);
            console.log('The exit signal was: ' + signal);
            console.log('finished');
        });
    }
    res.redirect('/polls')
};

exports.saveIpAddress = function (req, res) {
    var ip = req.params.ip;

    // init python shell
    var pyshell = new PythonShell('main.py', options);
    // enter to Deploy instances menu
    pyshell.send('1');
    // insert the configuration file
    pyshell.send('NodeApp/public/assets/Config_SecretSharing.json');
    // invoke get_aws_network_details_from_api
    pyshell.send('6');
    // send to python shell the online users ips
    pyshell.send(ip);
    //exit
    pyshell.send('4');

    pyshell.end(function (err, code, signal) {
            if(err) throw err;
            console.log('The exit code was: ' + code);
            console.log('The exit signal was: ' + signal);
            console.log('finished');
        });
    res.redirect('/polls');

};

exports.isReadyForPoll = function (req, res) {
    var pyshell = new PythonShell('main.py', options);

    // enter to Deploy instances menu
    pyshell.send('1');
    // insert the configuration file
    pyshell.send('NodeApp/public/assets/Config_SecretSharing.json');
    // invoke check_running_instances
    pyshell.send('7');
    // exit python shell
    pyshell.stdout.on('data', function (data) {
    // received a message sent from the Python script (a simple "print" statement)
        return data[data.lastIndexOf('*')-2];
    });
    pyshell.send('4');

    pyshell.end(function (err, code, signal) {
            if(err) throw err;
            console.log('The exit code was: ' + code);
            console.log('The exit signal was: ' + signal);
            console.log('finished');
        });
};

exports.isReadyForPollLoop= function(req, res){
  var numberOfOnline_servers = this.isReadyForPoll(req, res);
  var numberOfOnlineParties = req.session.NumberOfOnlineParties;

  while(numberOfOnline_servers < numberOfOnlineParties)
  {
      numberOfOnline_servers = this.isReadyForPoll(req, res);
  }
};

exports.executePoll = function (req, res) {
    // init python shell
    var pyshell = new PythonShell('main.py', options);
    // enter to Deploy instances menu
    pyshell.send('2');
    // insert the configuration file
    pyshell.send('NodeApp/public/assets/Config_SecretSharing.json');
    // invoke execute_poll
    pyshell.send('3');
    // exit python shell
    pyshell.send('4');

    pyshell.end(function (err, code, signal) {
            if(err) throw err;
            console.log('The exit code was: ' + code);
            console.log('The exit signal was: ' + signal);
            console.log('finished');
        });
};

exports.executePollAPI = function (req, res){
    var nOffline = req.session.NumberOfOfflineParties;
    var isReady = this.isReadyForPoll(req, res);
    while(nOffline < isReady)
    {
        isReady = this.isReadyForPoll(req, res);
    }

    // when the offline parties are ready, execute the poll

     // init python shell
    var pyshell = new PythonShell('main.py', options);
    // enter to Deploy instances menu
    pyshell.send('2');
    // insert the configuration file
    pyshell.send('NodeApp/public/assets/Config_SecretSharing.json');
    // invoke execute_poll
    pyshell.send('3');
    // exit python shell
    pyshell.send('4');

    pyshell.end(function (err, code, signal) {
            if(err) throw err;
            console.log('The exit code was: ' + code);
            console.log('The exit signal was: ' + signal);
            console.log('finished');
        });
};

exports.isPollCompleted = function (req, res) {
     // init python shell
    var pyshell = new PythonShell('main.py', options);
    // enter to Deploy instances menu
    pyshell.send('2');
    // insert the configuration file
    pyshell.send('NodeApp/public/assets/Config_SecretSharing.json');
    // invoke if poll is finished
    pyshell.send('5');
    // exit python shell
    pyshell.stdout.on('data', function (data) {
    // received a message sent from the Python script (a simple "print" statement)
        if(data.toString() === 'True')
        {
            res.redirect(200, 'polls/');
        }
        else
        {
            res.redirect(204, 'polls/');
        }
    });
    pyshell.send('4');

    pyshell.end(function (err, code, signal) {
            if(err) throw err;
            console.log('The exit code was: ' + code);
            console.log('The exit signal was: ' + signal);
            console.log('finished');
        });

};

exports.getMyId = function (req, res) {
    var ip = req.params.ip;
    var filePath = __dirname + '/../public/assets/parties.conf';

    fs.readFile(filePath, 'utf8', function (err, data) {
        if (err)
            return console.log(err);
        var splitedStrings = data.split('\n')
        for(var idx = 0; idx < splitedStrings.length; idx++)
        {
            if(splitedStrings[idx].indexOf(ip) > -1)
                res.json({'id': idx});
        }
    });
};

exports.getMyProxy = function(req, res)
{
    let id = req.params.id;
    var filePath = __dirname + '/../public/assets/proxies.conf';

    fs.readFile(filePath, 'utf8', function (err, data) {
        if (err)
            return console.log(err);
        var splitedStrings = data.split('\n')
        res.json({"proxyAddress": splitedStrings[idx]});
    });

};

//TODO add button for sign for experiments - experiments will be a document in db - contains the circuit the current parties file (including proxy)
//TODO I need to generate all the proxy using MATRIX