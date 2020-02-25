# DeepVentilation

This application connects to a Concept2 PM5 monitor and a SweetZpot FLOW
breathing sensor using Bluetooth Low Energy, and predicts airflow using a LSTM
neural netowrk model. 

## Requirements

Hardware:

* [SweetZpot FLOW breathing sensor](https://www.sweetzpot.com/flow).
* [PM5](https://www.concept2.com/indoor-rowers/performance-monitors) attached to a [Concept2 ergometer](https://www.concept2.com).

Software:

* [Web Bluetooth supported browser](https://caniuse.com/#feat=web-bluetooth).
* Python 3 for predicting airflow


## Usage

* Open `index.html` in a browser that supports Web Bluetooth (for example Google
  Chrome).
* On the PM5 monitor: **More Options** -> **Turn Wireless ON**
* Click the **Connect PM5** button in the web app. The PM5 should appear as
  a device; select it and click **Pair**.
* To connect the FLOW sensor(s), click **Connect FLOW abdomen/ribcage**,
  depending on the placement of your sensor. 
    - If you have several sensors, and are unable to distinguish them by their
      address, open *Developer tools* in the browser, click the **Test FLOW**
      button, and pair with one of your devices. The values from the sensor will
      be printed to the console, and you can individually test your sensors to
      see which is connected. Then click **Stop test FLOW**. After this you can
      click **Connect FLOW abdomen/ribcage**, and choose the sensor which is
      marked with *paired*; this is the one you connected to when testing.
* To connect a heart rate sensor (either using one of the FLOW sensors, or a
  separate heart rate sensor), click **Connect HR**, and pair with a compatible
  device.

The predicted airflow will appear when 5 seconds of breathing have been sampled.
The real time graphs of breathing data and predicted airflow will automatically
scale based on the maximum and minimum values obtained.


Tested in Google Chrome on Mac OS X.
