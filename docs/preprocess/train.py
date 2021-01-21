#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Train deep learning model to estimate power from breathing data.


Author:   
    Erik Johannes Husom

Created:  
    2020-09-16  

"""
import sys
import time

from kerastuner import HyperParameters
from kerastuner.tuners import Hyperband, RandomSearch
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.utils import plot_model
import yaml

from config import MODELS_PATH, MODELS_FILE_PATH, TRAININGLOSS_PLOT_PATH
from config import PLOTS_PATH
from model import DeepPowerHyperModel, cnn, dnn, lstm, cnndnn

def train(filepath):
    """Train model to estimate power.

    Args:
        filepath (str): Path to training set.

    """
    
    MODELS_PATH.mkdir(parents=True, exist_ok=True)

    # Load parameters
    params = yaml.safe_load(open("params.yaml"))["train"]
    net = params["net"]

    # Load training set
    train = np.load(filepath)

    X_train = train["X"]
    y_train = train["y"]

    n_features = X_train.shape[-1]

    # Create sample weights
    sample_weights = np.ones_like(y_train)

    if params["weigh_samples"]:
        sample_weights[y_train > params["weight_thresh"]] = params["weight"]

    hist_size = X_train.shape[-2]

    # hypermodel = DeepPowerHyperModel(hist_size, n_features)

    # # hp = HyperParameters()
    # # hp.Choice("num_layers", values=[1, 2])
    # # hp.Fixed("kernel_size", value=4)
    # # hp.Fixed("kernel_size_0", value=4)

    # tuner = Hyperband(
    #         hypermodel,
    #         # hyperparameters=hp,
    #         # tune_new_entries=True,
    #         objective="val_loss",
    #         # max_trials=10,
    #         # min_epochs=20,
    #         max_epochs=50,
    #         executions_per_trial=2,
    #         directory="model_tuning",
    #         project_name="DeepPower"
    # )

    # tuner.search_space_summary()

    # tuner.search(
    #     X_train, y_train, 
    #     epochs=params["n_epochs"], 
    #     batch_size=params["batch_size"],
    #     validation_split=0.2,
    #     sample_weight=sample_weights
    # )

    # tuner.results_summary()

    # # best_hyperparameters = tuner.get_best_hyperparameters(1)[0]

    # # model = tuner.hypermodel.build(best_hyperparameters)

    # # print(model.summary())

    # # history = model.fit(
    # #     X_train, y_train, 
    # #     epochs=params["n_epochs"], 
    # #     batch_size=params["batch_size"],
    # #     validation_split=0.2,
    # #     sample_weight=sample_weights
    # # )

    # model = tuner.get_best_models()[0]

    # print(model.summary())

    # model.save(MODELS_FILE_PATH)

    # Build model
    if net == "cnn":
        hist_size = X_train.shape[-2]
        model = cnn(hist_size, n_features,
                kernel_size=params["kernel_size"]
        )
    elif net == "dnn":
        model = dnn(n_features)
    elif net == "lstm":
        pass
    elif net == "cnndnn":
        pass

    print(model.summary())


    # Save a plot of the model
    plot_model(
        model,
        to_file=PLOTS_PATH / 'model.png',
        show_shapes=False,
        show_layer_names=True,
        rankdir='TB',
        expand_nested=True,
        dpi=96
    )

    history = model.fit(
        X_train, y_train, 
        epochs=params["n_epochs"], 
        batch_size=params["batch_size"],
        validation_split=0.2,
        sample_weight=sample_weights
    )

    model.save(MODELS_FILE_PATH)

    TRAININGLOSS_PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    n_epochs = range(len(loss))

    plt.figure()
    plt.plot(n_epochs, loss, label="Training loss")
    plt.plot(n_epochs, val_loss, label="Validation loss")
    plt.legend()
    plt.savefig(TRAININGLOSS_PLOT_PATH)


if __name__ == "__main__":

    np.random.seed(2020)

    train(sys.argv[1])
