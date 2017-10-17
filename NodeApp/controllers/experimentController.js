const express = require('express');
const formidable = require('formidable');
const path = require('path');
const uploadDir = path.join(__dirname, '/..', '/public/')
console.log(uploadDir);

exports.experiment_create_get = function (req, res, next) {
    res.render('experiment_form', { title: 'Create Experiment' });
};

exports.experiment_create_post = function (req, res) {
    var form = new formidable.IncomingForm();
    form.multiples = true
    form.keepExtensions = true
    form.uploadDir = uploadDir

    form.parse(req, (err, fields, files) =>
        {
            if (err) return res.status(500).json({ error: err })
            // res.status(200).json({ uploaded: true});
        })
    form.on('fileBegin', function (name, file) {
        const[fileName, fileExt] = file.name.split('.');
        console.log(file);
        file.path = path.join(uploadDir, `${fileName}_${new Date().getTime()}.${fileExt}`);

    });
    res.redirect('/experiments/experiment_execute');
};

