#!/usr/bin/env python3
"""Evaluate deep learning model to estimate power from breathing data.

Author:   
    Erik Johannes Husom

Created:  
    2020-09-17

"""
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras import models
import yaml

from config import METRICS_FILE_PATH, PLOTS_PATH, PREDICTION_PLOT_PATH, DATA_PATH


def evaluate(model_filepath, test_filepath):
    """Evaluate model to estimate power.

    Args:
        model_filepath (str): Path to model.
        test_filepath (str): Path to test set.

    """

    METRICS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Load parameters
    params = yaml.safe_load(open("params.yaml"))["evaluate"]
    smooth_targets = params["smooth_targets"]

    test = np.load(test_filepath)

    X_test = test["X"]
    y_test = test["y"]

    model = models.load_model(model_filepath)

    y_pred = model.predict(X_test)

    if smooth_targets > 1:
        y_pred = pd.Series(y_pred.reshape(-1)).rolling(smooth_targets).mean()
        y_pred.fillna(0, inplace=True)
        y_pred = np.array(y_pred)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("MSE: {}".format(mse))
    print("R2: {}".format(r2))

    results = model.evaluate(X_test, y_test)
    print(results)

    plot_prediction(y_test, y_pred, inputs=X_test, info="(MSE: {})".format(mse))

    with open(METRICS_FILE_PATH, "w") as f:
        json.dump(dict(mse=mse), f)


def plot_prediction(y_true, y_pred, inputs=None, info="", backend="plotly"):
    """Plot the prediction compared to the true targets.

    A matplotlib version of the plot is saved, while a plotly version by
    default is shown. To show the plot with matplotlib instead, the 'backend'
    parameter has to be changed to 'matplotlib'.

    Args:
        y_true (array): True targets.
        y_pred (array): Predicted targets.
        include_input (bool): Whether to include inputs in plot. Default=True.
        inputs (array): Inputs corresponding to the targets passed. If
            provided, the inputs will be plotted together with the targets.
        info (str): Information to include in the title string.
        backend (str): Whether to use matplotlib or plotly as plot backend.
            Default='plotly'.

    """

    PREDICTION_PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax1 = plt.subplots()

    ax1.set_xlabel("time step")
    ax1.set_ylabel("power (W)")

    ax1.plot(y_true, label="true")
    ax1.plot(y_pred, label="pred")

    if inputs is not None:
        input_columns = pd.read_csv(DATA_PATH / "input_columns.csv")

        if len(inputs.shape) == 3:
            n_features = inputs.shape[-1]
        elif len(inputs.shape) == 2:
            # If data is flattened, the number of input features are equal
            # to the length of input columns minus the  power column
            n_features = len(input_columns) - 1

        ax2 = ax1.twinx()
        ax2.set_ylabel("scaled units")
        print("==================")
        print(n_features)

        for i in range(n_features):
            # Plot the features of the last time step in each sequence. The
            # if/else block makes sure the indexing is done correctly based on
            # whether the data is sequentialized or not.
            if len(inputs.shape) == 3:
                print("==================")
                # print(inputs.shape)
                print(i)
                print(input_columns.iloc[i+1,1])
                ax2.plot(inputs[:, -1, i], label=input_columns.iloc[i+1,1])
            elif len(inputs.shape) == 2:
                ax2.plot(inputs[:, i-n_features], label=input_columns.iloc[i+1,1])
         

    fig.legend()

    plt.title("True vs pred " + info, wrap=True)
    plt.savefig(PREDICTION_PLOT_PATH)

    if backend == "matplotlib":
        plt.show()
    else:

        x = np.linspace(0, len(y_true)-1, len(y_true))
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        config = dict({'scrollZoom': True})

        fig.add_trace(
                go.Scatter(x=x, y=y_true.reshape(-1), name="true"),
                secondary_y=False,
        )

        fig.add_trace(
                go.Scatter(x=x, y=y_pred.reshape(-1), name="pred"),
                secondary_y=False,
        )

        if inputs is not None:
            input_columns = pd.read_csv(DATA_PATH / "input_columns.csv")
            
            if len(inputs.shape) == 3:
                n_features = inputs.shape[-1]
            elif len(inputs.shape) == 2:
                n_features = len(input_columns) - 1

            for i in range(n_features):

                if len(inputs.shape) == 3:
                    fig.add_trace(
                            go.Scatter(
                                x=x, y=inputs[:, -1, i],
                                name=input_columns.iloc[i+1, 1]
                            ),
                            secondary_y=True,
                    )
                elif len(inputs.shape) == 2:
                    fig.add_trace(
                            go.Scatter(
                                x=x, y=inputs[:, i-n_features],
                                name=input_columns.iloc[i+1, 1]
                            ),
                            secondary_y=True,
                    )

        fig.update_layout(title_text="True vs pred " + info)
        fig.update_xaxes(title_text="time step")
        fig.update_yaxes(title_text="Airflow", secondary_y=False)
        fig.update_yaxes(title_text="scaled units", secondary_y=True)

        fig.write_html(str(PLOTS_PATH / "prediction.html"))
        # fig.show(config=config)


if __name__ == "__main__":

    np.random.seed(2020)

    if len(sys.argv) < 3:
        try:
            evaluate("assets/models/model.h5", "assets/data/combined/test.npz")
        except:
            print("Could not find model and test set.")
            sys.exit(1)
    else:
        evaluate(sys.argv[1], sys.argv[2])
