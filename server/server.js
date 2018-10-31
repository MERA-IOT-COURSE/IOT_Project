"use strict";

const express = require("express");
const parser = require('body-parser');
const gpio = require("onoff").Gpio;
const application = express();

let pin = new gpio(17, 'out')

application.use(parser.json())
application.use(parser.urlencoded({ extended: true }));


application.get('/', (req, res) => {
    res.sendFile('index.html', { root: __dirname });
    return;
});

application.get('/gpio/get', (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.send(JSON.stringify({ status: pin.readSync() }));
    return;
});

application.post('/gpio/switch', (req, res) => {
    let status = +req.body.status;
    if (status === 0) {
        pin.write(gpio.LOW, () => {})
        console.log('OFF');
    }
    else {
        pin.write(gpio.HIGH, () => {})
        console.log('ON');
    }
    res.end();
    return;
});

application.listen(9999, '0.0.0.0');


/*
    let pin = new gpio(17, 'out')
    setInterval(() => {
        if (pin.readSync() === 0) {
            pin.write(gpio.HIGH, () => {})
            console.log('ON')
        }
        else {
            pin.write(gpio.LOW, () => {})
            console.log('OFF')
        }
    }, 100);
 */
