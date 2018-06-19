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

/*
* State has 4 values:
* 1. OPEN
* 2. CLOSED
* 3. RUN
* 4. COMPLETED
*/

exports.openForRegistration = function (req, res)
{
    if(isNaN(req.session.state))
    {
        req.session.state = "OPEN";
        req.session.pollName = req.params.pollName;
    }

    res.redirect('/polls');
};

exports.registerToPoll = function (req, res) {
    let pollName = req.session.pollName
    let clientIp = req.params.ip;
    let type = req.params.type;

    let client = redis.createClient();

    // insert ip address to addresses table
    client.rpush('addresses', clientIp, function (err) {
        if (err) console.log("Error in address registration");
    });

    client.rpush(pollName, clientIp.toString(), type.toString(),
        function (err) {
        if(err) console.log("Error in registration");
    });
    res.redirect('/polls');
};

exports.getPollsParams = function (req, res) {
    let jsonData = {table: []};

    let jsonObj = JSON.stringify(jsonData);

};

exports.changePollState = function (req, res) {

};

exports.closePollForRegistration = function (req, res) {
    req.session.state = "CLOSED";
    let pollName = req.session.pollName ;
    let client = redis.createClient(6379, "35.171.69.162");

    //retreive # of mobiles

    let numberOfMobiles = 0;
    client.lrange(pollName, 0, -1, function (err, reply) {
        if (err) console.log('Error retrieve poll data');
        console.log(typeof(reply));
        console.log(reply);

    });

    client.lrange('addresses', 0, -1, function (err, data) {
        if (err) console.log('Error retrieve addresses');

        //write addresses to file
        let fileName = __dirname + '/../public/assets/parties.conf';
        //delete file if exists
        fs.unlink(fileName, function (err) {
           console.log(err)
        });

        data.forEach(function (entry) {
            console.log(entry);
            fs.appendFileSync(fileName, entry + ":8000\n");
        })
    });
    res.redirect('/polls')
};