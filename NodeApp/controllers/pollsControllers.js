var formidable = require('formidable');
var spawn = require('child_process').spawn;


exports.prepareOnline = function (req, res) {
    var form = new formidable.IncomingForm();
    form.multiples = true;
    form.keepExtensions = true;

    form.parse(req, function(err, fields) {
        var pollName =  fields['name'];
        var numberOfOnlineParties =  fields['numberOfOnlineParties'];
        var numberOfOfflineParties =  fields['numberOfOfflineParties'];
        var arr = fields['IPs'].split(",");
        // sessionStorage.setItem('IPs', fields['IPs']);
        // sessionStorage.setItem('pollName', pollName);
        // sessionStorage.setItem('numberOfOnlineParties', numberOfOnlineParties);
        // sessionStorage.setItem('numberOfOfflineParties', numberOfOfflineParties);
    });
    setTimeout(function () {
        var child = spawn('/usr/bin/nodejs');
        child.stdin.write("console.log('Hey')\n");
        child.stdin.end();

    }, 100);
    // var options = {shell: true};
    // var scriptExec = spawn('python3', ['../main.py'], options);
    // scriptExec.stdin.setEncoding('utf-8');
    // // scriptExec.stdout.pipe(scriptExec.stdout);
    // scriptExec.stdin.write('1\n');
    // scriptExec.stdin.write('public/assets/Config_SecretSharing.json\n');
    // scriptExec.stdin.write('1\n');
    // scriptExec.stdin.end();
    // scriptExec.stdout.on('error', function (err) {
    //     console.log(err);

    // });

    // scriptExec.stderr.on('error', function (err) {
    //     console.log(err);
    // })
    // pythonProc.send('1');

    res.redirect('/polls');
};

exports.isReadyForPoll = function (req, res) {
    spawn('python3', []);
};

exports.executePoll = function (req, res) {
    spawn('python3', []);
};

exports.isPollFinished = function (req, res) {
    spawn('python3', []);
};