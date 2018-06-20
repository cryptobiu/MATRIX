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
    //party id
    //proxy server address
    //link to circuit
    let ip = req.params.ip;
    let jsonData = {table: []};
    let client = redis.createClient();
    client.lrange('mappings', 0, -1, function (err, data) {
        for (let idx = 0; idx < data.length; idx +=3)
        {
            if(data[idx] === ip)
            {
                jsonData.table.push({'proxyAddress': data[idx + 1], 'partyId': data[idx + 2]})
                break;
            }
        }
    });

    let jsonObj = JSON.stringify(jsonData);
    res.write(jsonObj);
};

exports.changePollState = function (req, res) {

};

exports.closePollForRegistration = function (req, res) {
    req.session.state = "CLOSED";
    let pollName = req.params.pollName ;
    let client = redis.createClient();

    //retreive # of mobiles

    let numberOfMobiles = 0;
    let mobilesIps = [];
    let idx = 0;
    client.lrange(pollName, 0, -1, function (err, data) {
        if (err) console.log('Error retrieve poll data');
        for (idx = 0; idx < data.length; idx += 2)
        {
            if (data[idx] === 'online_mobile')
            {
                let mobileIp = data[idx + 1];
                client.lrem('addresses', 0, mobileIp, function (err) {
                    if(err) console.log("Error removing mobile ip");
                });
                //push to mapping table ip proxy _server_address party_id
                client.rpush('mappings', mobileIp, '34.239.19.87', numberOfMobiles, function (err) {
                    if(err) console.log("Error pushing data to mapping");
                });
                mobilesIps.push(mobileIp);
                numberOfMobiles += 1;
            }
        }
    });

    let partiesSize = 0;
    client.lrange('addresses', 0, -1, function (err, data) {
        if (err) console.log('Error retrieve addresses');

        //write addresses to file
        let fileName = __dirname + '/../public/assets/parties.conf';
        //delete file if exists
        fs.unlink(fileName, function (err) {console.log(err)});

        if(numberOfMobiles > 0)
        {
            for(let idx = 0; idx < numberOfMobiles; idx++)
            {
                fs.appendFileSync(fileName, '34.239.19.87:' + (9000 + idx * 100).toString());
            }
        }

        data.forEach(function (entry) {
            console.log(entry);
            fs.appendFileSync(fileName, entry + ":8000\n");
            partiesSize += 1;
        });

        let exec = require('child_process').exec;
        let createCircuit = 'java -jar ' + __dirname + '/../public/assets/GenerateArythmeticCircuitForVariance.jar '
            + partiesSize + ' 3';
        exec(createCircuit, function (error, stdout){
            if(error) console.log('Error: ' + error);
            console.log(stdout);
        });
        //copy the circuit to the public path
        let copyCommand = 'cp ' + __dirname + ' ArythmeticVarianceFor3InputsAnd' + partiesSize + 'Parties.txt' +
            ' ' + __dirname + '/../public/assets/';
        exec(copyCommand, function (error, stdout) {
            if(error) console.log('Error: ' + error);
            console.log(stdout);
        });
    });
    res.redirect('/polls')
};