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
    let pollName = req.params.pollName;
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
    let pollName = req.params.pollName;
    let ip = req.params.ip;
    let jsonData = {};
    let client = redis.createClient();
    client.lrange('execution' + pollName, 0, -1, function (err, data) {
        if(err) console.log(err);
        console.log(data.length);
        for (let idx = 0; idx < data.length; idx+=20)
        {
            if(data[idx] === ip)
            {
                for(let idx2 = idx + 2; idx2 < 19; idx2+=2)
                    jsonData[data[idx2]] = data[idx2 + 1];
                break
            }
        }
        jsonData['circuitFileAddress'] =  'http://35.171.69.162/polls/circuit/';

        res.json(jsonData);
    });


};

exports.changePollState = function (req, res) {

};

exports.closePollForRegistration = function (req, res) {
    req.session.state = "CLOSED";
    let pollName = req.params.pollName ;
    let client = redis.createClient();

    let numberOfMobiles = 0;
    let mobilesIps = [];
    let idx = 0;
    client.lrange(pollName, 0, -1, function (err, data) {
        if (err) console.log('Error retrieve poll data');
        for (idx = 0; idx < data.length; idx += 2)
        {
            if (data[idx + 1] === 'online_mobile')
            {
                let mobileIp = data[idx];
                // client.lrem('addresses', 0, mobileIp, function (err) {
                //     if(err) console.log("Error removing mobile ip");
                // });

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
        let offlineUsers = [];

        // data.forEach(function (entry) {
        // TODO continue over number of mobiles becuase they were not deleted
        //     fs.appendFileSync(fileName, entry + ":8000\n");
        //     partiesSize += 1;
        //     offlineUsers.push(entry);
        // });

        partiesSize += numberOfMobiles;

        let exec = require('child_process').exec;
        let createCircuit = 'java -jar ' + __dirname + '/../public/assets/GenerateArythmeticCircuitForVariance.jar '
            + partiesSize.toString() + ' 3';
        exec(createCircuit, function (error, stdout){
            if(error) console.log('Error: ' + error);
            console.log(stdout);
        });

        //copy the circuit to the public path
        let circuitName = 'ArythmeticVarianceFor3InputsAnd' + partiesSize + 'Parties.txt'

         // for each entry save the exact cli parameters

    for(let mobilesIdx = 0; mobilesIdx < numberOfMobiles; mobilesIdx++)
    {
        let jsonData = {};
        jsonData['partyID'] = mobilesIdx.toString();
        jsonData['partiesNumber'] = partiesSize.toString();
        jsonData['inputFile'] = 'inputSalary' + mobilesIdx + '.txt';
        jsonData['outputFile'] = 'output.txt';
        jsonData['circuitFile'] = circuitName;
        jsonData['proxyAddress'] = '34.239.19.87';
        jsonData['fieldType'] = 'ZpMersenne';
        jsonData['internalIterationsNumber'] = '1';
        jsonData['NG'] = '1';
        let dataFileName =  __dirname + '/../public/assets/' + mobilesIps[mobilesIdx]+'.json';
        fs.writeFile(dataFileName, JSON.stringify(jsonData), 'utf8', function (err) {
            if (err) console.log(err);
        });

        // client.rpush('execution' + pollName, mobilesIps[mobilesIdx], pollName, 'partyID', mobilesIdx, 'partiesNumber',
        //     partiesSize, 'inputFile', 'inputSalary' + mobilesIdx + '.txt', 'outputFile', 'output.txt', 'circuitFile',
        //     circuitName, 'proxyAddress', '34.239.19.87', 'fieldType', 'ZpMersenne', 'internalIterationsNumber', '1',
        //     'NG', '1', function (err) {console.log(err)});
    }

    // for(let offlineIdx = 0; offlineIdx < offlineUsers.length; offlineIdx++)
    // {
    //     client.rpush('execution' + pollName, offlineUsers[offlineIdx], pollName, 'partyID', offlineIdx, 'partiesNumber',
    //         partiesSize, 'inputFile', 'inputSalary' + offlineIdx + '.txt', 'outputFile', 'output.txt', 'circuitFile',
    //         circuitName, 'partiesFile', 'parties.conf', 'fieldType', 'ZpMersenne', 'internalIterationsNumber', '1',
    //         'NG', '1', function (err) {console.log(err)});
    // }
    let copyCommand = 'cp ' + __dirname + ' ' + circuitName + ' ' + __dirname + '/../public/assets/';
        exec(copyCommand, function (error, stdout) {
            if(error) console.log('Error: ' + error);
            console.log(stdout);
        });
    });



    res.redirect('/polls')
};