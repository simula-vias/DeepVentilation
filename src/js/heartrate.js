/* 
Web bluetooth api script for BreathZpot sensors. 
Adapted from the following source: https://googlechrome.github.io/samples/web-bluetooth/notifications-async-await.html

Copyright 2019 Eigil Aandahl

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

*/

var heartRateCharacteristic;
// var heartRateConnected = false;

async function onHeartRateButtonClick() {

    // if (heartRateConnected) {
    //     onStopHeartRateClick();
    //     document.querySelector('#connect-hr').innerText = 'Connect HR';
    // } else {

        let serviceUuid = 0x180d; // Heart rate service
        serviceUuid = parseInt(serviceUuid);

        let characteristicUuid = 0x2a37; // Heart rate characteristic
        characteristicUuid = parseInt(characteristicUuid);

        try {
            console.log('Requesting Bluetooth Device...');
            const device = await navigator.bluetooth.requestDevice({
                filters: [{services: [serviceUuid]}]});

            console.log('Connecting to GATT Server...');
            const server = await device.gatt.connect();

            console.log('Getting Service...');
            const service = await server.getPrimaryService(serviceUuid);

            console.log('Getting Characteristic...');
            heartRateCharacteristic = await service.getCharacteristic(characteristicUuid);

            await heartRateCharacteristic.startNotifications();

            // heartRateConnected = true;
            // document.querySelector('#connect-hr').innerText = 'Disconnect HR';

            console.log('> Notifications started');
            heartRateCharacteristic.addEventListener('characteristicvaluechanged',
                handleHeartRateNotifications);

        
        } catch(error) {
            console.log('Argh! ' + error);
        }
    // }
    
}


async function onStopHeartRateClick() {
  if (heartRateCharacteristic) {
    try {
      await heartRateCharacteristic.stopNotifications();
      console.log('> Notifications stopped');
      heartRateCharacteristic.removeEventListener('characteristicvaluechanged',
          handleHeartRateNotifications);
    } catch(error) {
      console.log('Argh! ' + error);
    }
  }
}


var heartRateValues = [];
var heartRateText = document.querySelector('#heartRateText');
var heartRateCanvas = document.querySelector('#heartRateChart');

// Function handleHeartRateNotifications() is inspired by the heart rate demo made by the Web
// Bluetooth Community group:
// https://webbluetoothcg.github.io/demos/heart-rate-sensor/
function handleHeartRateNotifications(event) {
  // In Chrome 50+, a DataView is returned instead of an ArrayBuffer.
    let value = event.target.value;
    value = value.buffer ? value : new DataView(value);
    let id = event.target.service.device.id;
    let timestamp = new Date().getTime();
    let flags = value.getUint8(0);
    let rate16Bits = flags & 0x1;
    let result = {};
    let index = 1;
    if (rate16Bits) {
        result.heartRate = value.getUint16(index, /*littleEndian=*/true);
        index += 2;
    } else {
        result.heartRate = value.getUint8(index);
        index += 1;
    }
    let contactDetected = flags & 0x2;
    let contactSensorPresent = flags & 0x4;
    if (contactSensorPresent) {
        result.contactDetected = !!contactDetected;
    }
    let energyPresent = flags & 0x8;
    if (energyPresent) {
        result.energyExpended = value.getUint16(index, /*littleEndian=*/true);
        index += 2;
    }
    let rrIntervalPresent = flags & 0x10;
    if (rrIntervalPresent) {
        let rrIntervals = [];
        for (; index + 1 < value.byteLength; index += 2) {
            rrIntervals.push(value.getUint16(index, /*littleEndian=*/true));
            // socket.emit('message', new Date().getTime() + ',rr,' + value.getUint16(index, true)); 
        }
        result.rrIntervals = rrIntervals;
    }
    // socket.emit('message', timestamp + ',heartrate,' + result.heartRate); 

    heartRateText.innerHTML = result.heartRate + ' &#x2764;';
    heartRateValues.push(result.heartRate);

    if (heartRateValues.length > 20) {
        heartRateValues.shift();
    }

    drawWaves(heartRateValues, heartRateCanvas, 200, 60, 70);
}

