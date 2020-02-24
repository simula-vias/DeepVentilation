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

var testFlowCharacteristic;
var testFlowConnected = false;

async function onTestButtonClick() {

    if (testFlowConnected) {
        onStopTestFlowClick();
        document.querySelector('#test-flow').innerText = 'Test FLOW';
    } else {

        let serviceUuid = 0xffb0; // BreathZpot breathing service
        // let serviceUuid = 0x180d; // BreathZpot breathing service
        serviceUuid = parseInt(serviceUuid);

        let characteristicUuid = 0xffb3; // BreathZpot breathing characteristic
        // let characteristicUuid = 0x2a37; // BreathZpot breathing characteristic
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
            testFlowCharacteristic = await service.getCharacteristic(characteristicUuid);

            await testFlowCharacteristic.startNotifications();

            testFlowConnected = true;
            document.querySelector('#test-flow').innerText = 'Stop test FLOW';

            console.log('> Notifications started');
            testFlowCharacteristic.addEventListener('characteristicvaluechanged',
                handleTestNotifications);

        
        } catch(error) {
            console.log('Argh! ' + error);
        }
    }
    
}

function handleTestNotifications(event) {

    let value = event.target.value;
    let int16View = new Int16Array(value.buffer);
    // TextDecoder to process raw data bytes.
    for (let i = 0; i < 7; i++) {
        //Takes the 7 first values as 16bit integers from each notification
        //This is then sent as a string with a sensor signifier as OSC using osc-web
        console.log(int16View[i].toString())
    }
}

async function onStopTestFlowClick() {
  if (testFlowCharacteristic) {
    try {
      await testFlowCharacteristic.stopNotifications();
      console.log('> Notifications stopped');
      testFlowCharacteristic.removeEventListener('characteristicvaluechanged',
          handleTestNotifications);
    } catch(error) {
      console.log('Argh! ' + error);
    }
  }
}

