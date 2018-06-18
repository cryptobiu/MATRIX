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
* State has 3 values:
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
    let pollName = req.params.pollName;
    let clientIp = req.params.ip;
    let type = req.params.type;

    let client = redis.createClient();

    // insert ip address to addresses table
    client.lpush('addresses', clientIp);

    client.lpush(pollName, clientIp.toString(), type.toString(),
        function (err) {
        if(err)
        {
            console.log("Error in registartion");
        }

    });
    res.redirect('/polls');
};

exports.getPollsParams = function (req, res) {

};

exports.changePollState = function (req, res) {

};