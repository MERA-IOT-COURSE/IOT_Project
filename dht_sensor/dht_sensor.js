"use strict";

const blynkLib = require('blynk-library');
const sensorLib = require('node-dht-sensor');

let AUTH = 'YOUR_AUTH_TOKEN';
// Setup Blynk
let blynk = new blynkLib.Blynk(AUTH);
// Setup sensor, exit if failed
let sensorType = 22; // 11 for DHT11, 22 for DHT22 and AM2302
let sensorPin  = 2;  // The GPIO pin number for sensor signal

if (!sensorLib.initialize(sensorType, sensorPin)) {
    console.warn('Failed to initialize sensor');
    process.exit(1);
}

// Automatically update sensor value every 2 seconds
setInterval(function() {
    let readout = sensorLib.read();
    blynk.virtualWrite(3, readout.temperature.toFixed(2));
    blynk.virtualWrite(4, readout.humidity.toFixed(2));
          
    console.log('Temperature:', readout.temperature.toFixed(1) + 'C');
    console.log('Humidity:   ', readout.humidity.toFixed(1)    + '%');
}, 1000);

