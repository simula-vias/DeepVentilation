# DeepVentilation

This application connects to a Concept2 PM5 monitor and SweetZpot FLOW breathing
sensors using Bluetooth Low Energy, and predicts airflow using a LSTM neural
network model. 

## Requirements

Hardware:

* [SweetZpot FLOW breathing sensor](https://www.sweetzpot.com/flow).
* [PM5](https://www.concept2.com/indoor-rowers/performance-monitors) attached to a [Concept2 BikeErg](https://www.concept2.com).

Software:

* [Web Bluetooth supported browser](https://caniuse.com/#feat=web-bluetooth).
* Python 3 for predicting airflow, with the following modules:
    - pytorch
    - flask
    - numpy



## Usage

* Start airflow prediction app by running `python app.py` from the `src`
  directory.
* Open `index.html` in a browser that supports Web Bluetooth (for example Google
  Chrome).
* Connecting FLOW sensors:
    * **Important:** Strap the FLOW sensors around your abdomen/ribcage **before**
      you connect them to the web app. Otherwise the scaling of the data and the
      visualization will be suboptimal.
    * Click **Connect FLOW abdomen**, and pair with your device. The airflow
      model is based on abdominal movement, so the sensor needs to be placed
      around the waist to get accurate predictions. The predicted airflow will
      appear when 5 seconds of breathing have been sampled.
    * To get breathing measurements from ribcage movement as well, place another
      sensor around the ribcage, click **Connect FLOW ribcage** and pair with the
      second sensor.
    - *Tips*: If you have several sensors, and are unable to distinguish them by their
      address, open *Developer tools* in the browser, click the **Test FLOW**
      button, and pair with one of your devices. The values from the sensor will
      be printed to the console, and you can individually test your sensors to
      see which is connected. Click **Stop test FLOW** when you have identified
      the paired sensor. After this you can click **Connect FLOW
      abdomen/ribcage**, and choose the sensor which is marked with *paired*;
      this is the one you connected to when testing.
    - The real time graphs of breathing data and predicted airflow will
      automatically scale based on the maximum and minimum values obtained.
* Connecting PM5 BikeErg:
    * On the PM5 monitor, depending on your model: 
        - **More Options**  -> **Turn Wireless ON** *or*
        - **Connect**.
    * Click the **Connect PM5** button in the web app. The PM5 should appear as
      a device; select it and click **Pair**. Power data will appear when you start
      cycling. Additional workout data will appear below the graphs.
* Connecting heart rate sensor (either using one of the FLOW sensors, or a
  separate heart rate sensor): 
  * Click **Connect HR**, and pair with a compatible device.



Tested in Google Chrome on Mac OS X.
