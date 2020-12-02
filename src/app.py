#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real-time prediction tool for DeepVentilation.

Author:   
    Erik Johannes Husom

Created:  
    2020-12-02

"""
import time

from flask import Flask, abort, jsonify
from flask import request
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras import models

app = Flask(__name__)

PATH = "model/"
hist_size = 50

@app.route("/")
def index():
    return "Hello, World!"

"""
Input : array of breathing value of the size of historic_size
Output: airflow estimation + time of execution
"""
@app.route("/getEstimation", methods=["POST"])
def getEstimation():
    t = time.time()
    print(request.json)
    if not request.json or not "value" in request.json or len(request.json["value"]) != hist_size:
        abort(400)

    X = np.array(request.json["value"]).reshape(-1, 1)
    X = preprocess(X)
    X = scale(X)
    print(scaler)
    print(X)
    print(X.shape)

    y = [0]
    t = time.time() - t 
    return jsonify({"airflow" : str(y[0]),"time" : str(t)})


def preprocess(X):
    """Preprocess input data.

    Args:
        X (numpy array): Input.

    Returns:
        numpy array: Preprocessed inputs.

    """
    range_smoothing = 1
    slope_shift = 1

    df = pd.DataFrame(X, columns=["ribcage"])
    df.dropna(inplace=True)

    df["ribcage_gradient"] = np.gradient(df["ribcage"])

    df["ribcage_slope_sin"] = np.sin(
            calculate_slope(df["ribcage"], shift=1,
                rolling_mean_window=1, absvalue=False)
    )
    df["ribcage_slope_cos"] = np.cos(
            calculate_slope(df["ribcage"], shift=1,
                rolling_mean_window=1, absvalue=False)
    )

    del df["ribcage"]

    df.fillna(method="bfill", inplace=True)

    return np.array(df)

def scale(X):
    """Scale inputs.

    Args:
        X (numpy array): Inputs to scale.

    """

    return scaler.transform(X)

def calculate_slope(data, shift=1, rolling_mean_window=1, absvalue=False):
    """Calculate slope.

    Args:
        data (array): Data for slope calculation.
        shift (int): How many steps backwards to go when calculating the slope.
            For example: If shift=2, the slope is calculated from the data
            point two time steps ago to the data point at the current time
            step.
        rolling_mean_window (int): Window for calculating rolling mean.

    Returns:
        slope (array): Array of slope angle.

    """

    v_dist = data - data.shift(shift)
    h_dist = 0.1 * shift

    slope = np.arctan(v_dist / h_dist)

    if absvalue:
        slope = np.abs(slope)

    slope = slope.rolling(rolling_mean_window).mean()

    return slope


"""
This function load all the models form the file one time before the lauch of the app 
"""
if __name__ == "__main__":
    # Load scaler
    scaler = joblib.load(PATH + "scaler.sav")
    print("Scaler load successfully")

    # Load model
    model = models.load_model(PATH + "model.h5")
    print("Model successfully")
    print(model.summary())

    # Start the app
    app.run(debug=True, port=5000)


