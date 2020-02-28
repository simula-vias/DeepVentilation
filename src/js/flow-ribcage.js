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

var flowRibcageCharacteristic;
var ribcageValues = [];
var airflowValues = [];
var maxRibVal = 0;
var minRibVal = 4096;
var minAirVal = 0.1;
var maxAirVal = 0.0;
var ribcageCanvas = document.querySelector('#ribcageChart');
var airflowCanvas = document.querySelector('#airflowChart');

async function onFlowRibcageButtonClick() {

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
        flowRibcageCharacteristic = await service.getCharacteristic(characteristicUuid);

        await flowRibcageCharacteristic.startNotifications();

        console.log('> Notifications started');
        flowRibcageCharacteristic.addEventListener('characteristicvaluechanged',
            handleFlowRibcageNotifications);

    
    } catch(error) {
        console.log('Argh! ' + error);
    }

}

async function onStopFlowRibcageClick() {
  if (flowRibcageCharacteristic) {
    try {
      await flowRibcageCharacteristic.stopNotifications();
      console.log('> Notifications stopped');
      flowRibcageCharacteristic.removeEventListener('characteristicvaluechanged',
          handleFlowRibcageNotifications);
    } catch(error) {
      console.log('Argh! ' + error);
    }
  }
}

function handleFlowRibcageNotifications(event) {
    let value = event.target.value;
    let id = event.target.service.device.id;
    let int16View = new Int16Array(value.buffer);
    let timestamp = new Date().getTime();
    // TextDecoder to process raw data bytes.
    for (let i = 0; i < 7; i++) {

        let v = int16View[i];

        if (v > maxRibVal) {
            maxRibVal = v;
        }
        if (v < minRibVal) {
            minRibVal = v;
        }

        ribcageValues.push(int16View[i]);
    }
    // ribcageText.innerHTML = "Ribcage movement: " + int16View[0].toString();
    
    // let minRibVal = Math.min.apply(null, ribcageValues);
    // let maxRibVal = Math.max.apply(null, ribcageValues);
    let ribcageRange = maxRibVal - minRibVal;
    var ribcagePlotValues = ribcageValues.map(function(element) {
        return (element - minRibVal)/ribcageRange;
    });

    if (ribcagePlotValues.length > 455) {
    // if (ribcagePlotValues.length > 200) {
        ribcageValues.splice(0, 7);
    }
    drawWaves(ribcagePlotValues, ribcageCanvas, 1, 6.0);

    // Predicting airflow
    if (ribcageValues.length > 50 ){

        // let inputValues = ribcageValues.slice(-51, -1).map(function(element) {
            // return (

        fetch('http://127.0.0.1:5000/getEstimation', {
          method: 'post',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({'value': ribcagePlotValues.slice(-51, -1)})
        })
        .then((response) => response.json())
        .then((data) => {
          console.log('Success:', data);
            
            airflowValues.push(data.airflow);

            if (data.airflow > maxAirVal) {
                maxAirVal = data.airflow;
            }
            if (data.airflow < minAirVal) {
                minAirVal = data.airflow;
            }
            let airflowRange = maxAirVal - minAirVal;

            var airflowPlotValues = airflowValues.map(function(element) {
                return (element - minAirVal)/airflowRange;
            });

            // let a = airflowPlotValues.slice(-1);
            // a = a*200 - 100;

            // airflowText.innerHTML = "Predicted airflow: " + airflowValues.slice(-1);
            // airflowText.innerHTML = "Predicted airflow: " + Math.round(a);

            drawWaves(airflowPlotValues, airflowCanvas, 1, 42, 70);
                
        })
        .catch((error) => {
          console.error('Error:', error);
        });
        
    } 

    if (airflowValues.length > 64) {
        airflowValues.shift();
    }
}

