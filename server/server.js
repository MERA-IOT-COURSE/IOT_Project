"use strict";

const express = require("express")
const gpio = require("onoff").Gpio
const application = express()

application.get('/:name', (req, res) => {
     res.send(`Hello, ${req.params.name}`);
});


let pin = new gpio(17, 'out')
setInterval(() => {
    if (pin.readSync() === 0) {
	pin.write(gpio.HIGH, () => {})
	//console.log('ON')
    }
    else {
	pin.write(gpio.LOW, () => {})
	//console.log('OFF')
    }
}, 100);


//application.listen(9999, '0.0.0.0')


