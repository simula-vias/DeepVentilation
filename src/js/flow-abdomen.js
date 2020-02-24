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

var flowCharacteristic;
var abdomenValues = [];
var airflowValues = [];
var maxAbVal = 0;
var minAbVal = 4096;
var abdomenCanvas = document.querySelector('#abdomenChart');
var airflowCanvas = document.querySelector('#airflowChart');

async function onFlowButtonClick() {

    let serviceUuid = 0xffb0; // BreathZpot breathing service
    serviceUuid = parseInt(serviceUuid);

    let characteristicUuid = 0xffb3; // BreathZpot breathing characteristic
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
        flowCharacteristic = await service.getCharacteristic(characteristicUuid);

        await flowCharacteristic.startNotifications();

        console.log('> Notifications started');
        flowCharacteristic.addEventListener('characteristicvaluechanged',
            handleFlowNotifications);

    
    } catch(error) {
        console.log('Argh! ' + error);
    }
    
}

async function onStopFlowClick() {
  if (flowCharacteristic) {
    try {
      await flowCharacteristic.stopNotifications();
      console.log('> Notifications stopped');
      flowCharacteristic.removeEventListener('characteristicvaluechanged',
          handleFlowNotifications);
    } catch(error) {
      console.log('Argh! ' + error);
    }
  }
}

function handleFlowNotifications(event) {
    let value = event.target.value;
    let id = event.target.service.device.id;
    let int16View = new Int16Array(value.buffer);
    let timestamp = new Date().getTime();
    // TextDecoder to process raw data bytes.
    for (let i = 0; i < 7; i++) {
        //Takes the 7 first values as 16bit integers from each notification
        //This is then sent as a string with a sensor signifier as OSC using osc-web
        // socket.emit('message', timestamp + ',abdomen,' + int16View[i].toString()); 

        let v = int16View[i];

        if (v > maxAbVal) {
            maxAbVal = v;
        }
        if (v < minAbVal) {
            minAbVal = v;
        }

        abdomenValues.push(int16View[i]);
    }
    abdomenText.innerHTML = "Abdomen: " + int16View[0].toString();

    let abdomenRange = maxAbVal - minAbVal;
    var abdomenPlotValues = abdomenValues.map(function(element) {
        return (element - minAbVal)/abdomenRange;
    });

    if (abdomenValues.length > 200) {
        abdomenValues.splice(0, 7);
    }
    drawWaves(abdomenPlotValues, abdomenCanvas, 1, 6.0);

    // Predicting airflow
    if (abdomenValues.length > 50 ){
        fetch('http://127.0.0.1:5000/getEstimation', {
          method: 'post',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({'value': abdomenValues.slice(-51, -1)})
        })
        .then((response) => response.json())
        .then((data) => {
          console.log('Success:', data);
            airflowValues.push(data.airflow);
            airflowText.innerHTML = "Predicted airflow: " + data.airflow;
            drawWaves(airflowValues, airflowCanvas, 0.2, 42);
                
        })
        .catch((error) => {
          console.error('Error:', error);
        });
        

    } else {
        airflowValues.push(0);
        drawWaves(airflowValues, airflowCanvas, 0.2, 42);
    }

    if (airflowValues.length > 28) {
        airflowValues.shift();
    }
}

