#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Creating deep learning model for estimating power from breathing.

Author:
    Erik Johannes Husom

Date:
    2020-09-16

"""
from kerastuner import HyperModel
from tensorflow.keras import layers
from tensorflow.keras import models

from tensorflow.random import set_seed

def cnn(input_x, input_y, 
        n_steps_out=1, 
        seed=2020,
        kernel_size=2
    ):
    """Define a CNN model architecture using Keras.

    Args:
        input_x (int): Number of time steps to include in each sample, i.e. how
            much history is matched with a given target.
        input_y (int): Number of features for each time step in the input data.
        n_steps_out (int): Number of output steps.
        seed (int): Seed for random initialization of weights.
        kernel_size (int): Size of kernel in CNN.

    Returns:
        model (keras model): Model to be trained.

    """

    set_seed(seed)

    kernel_size = kernel_size

    model = models.Sequential()
    model.add(
        layers.Conv1D(
            filters=64,
            kernel_size=kernel_size,
            activation="relu",
            input_shape=(input_x, input_y),
            name="input_layer"
        )
    )
    model.add(layers.Conv1D(filters=64, kernel_size=kernel_size,
        activation="elu", name="conv1d_1"))
    model.add(layers.Conv1D(filters=64, kernel_size=kernel_size,
        activation="relu", name="conv1d_2"))
    # model.add(layers.MaxPooling1D(pool_size=2, name="pool_1"))
    model.add(layers.Dropout(rate=0.2))
    model.add(layers.Flatten(name="flatten"))
    model.add(layers.Dense(128, activation="relu", name="dense_1"))
    model.add(layers.Dense(64, activation="relu", name="dense_2"))
    # model.add(layers.Dense(32, activation="relu", name="dense_3"))
    model.add(layers.Dense(n_steps_out, activation="linear",
        name="output_layer"))
    model.compile(optimizer="adam", loss="mse", metrics=["mae", "mape"])

    return model


class DeepPowerHyperModel(HyperModel):

    def __init__(self, input_x, input_y, n_steps_out=1):
        """Define size of model.

        Args:
            input_x (int): Number of time steps to include in each sample, i.e. how
                much history is matched with a given target.
            input_y (int): Number of features for each time step in the input data.
            n_steps_out (int): Number of output steps.

        """

        self.input_x = input_x
        self.input_y = input_y
        self.n_steps_out = n_steps_out

    def build(self, hp, seed=2020):
        """Build model.

        Args:
            hp: HyperModel instance.
            seed (int): Seed for random initialization of weights.

        Returns:
            model (keras model): Model to be trained.

        """

        set_seed(seed)

        model = models.Sequential()
        model.add(
            layers.Conv1D(
                input_shape=(self.input_x, self.input_y),
                # filters=64,
                filters=hp.Int(
                    "filters",
                    min_value=16,
                    max_value=256,
                    step=32,
                    default=64),
                # kernel_size=hp.Int(
                #     "kernel_size",
                #     min_value=2,
                #     max_value=6,
                #     step=2,
                #     default=4),
                kernel_size=4,
                activation="relu",
                name="input_layer",
                padding="same"
            )
        )

        for i in range(hp.Int("num_conv1d_layers", 1, 3, default=1)):
            model.add(layers.Conv1D(
                # filters=64,
                filters=hp.Int(
                    "filters_" + str(i),
                    min_value=16,
                    max_value=256,
                    step=32,
                    default=64), 
                # kernel_size=hp.Int(
                #     "kernel_size_" + str(i),
                #     min_value=2,
                #     max_value=6,
                #     step=2,
                #     default=4),
                kernel_size=4,
                activation="relu", 
                name=f"conv1d_{i}"
            ))

        # model.add(layers.MaxPooling1D(pool_size=2, name="pool_1"))
        # model.add(layers.Dropout(rate=0.2))
        model.add(layers.Flatten(name="flatten"))

        for i in range(hp.Int("num_dense_layers", 1, 3, default=2)):
            model.add(layers.Dense(
                # units=64,
                units=hp.Int(
                    "units_" + str(i),
                    min_value=32,
                    max_value=256,
                    step=32,
                    default=64), 
                activation="relu",
                name=f"dense_{i}"
            ))

        model.add(layers.Dense(self.n_steps_out, activation="linear",
            name="output_layer"))
        model.compile(optimizer="adam", loss="mse", metrics=["mae", "mape"])

        return model

def dnn(input_x, n_steps_out=1, seed=2020):
    """Define a DNN model architecture using Keras.

    Args:
        input_x (int): Number of features.
        n_steps_out (int): Number of output steps.

    Returns:
        model (keras model): Model to be trained.

    """

    set_seed(seed)

    model = models.Sequential()
    model.add(layers.Dense(256, activation='relu', input_dim=input_x))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(n_steps_out, activation='linear'))
    model.compile(optimizer='adam', loss='mae')

    return model

def lstm(hist_size, n_features, n_steps_out=1):
    """Define a LSTM model architecture using Keras.

    Args:
        hist_size (int): Number of time steps to include in each sample, i.e.
            how much history should be matched with a given target.
        n_features (int): Number of features for each time step, in the input
            data.

    Returns:
        model (Keras model): Model to be trained.

    """

    model = models.Sequential()
    model.add(layers.LSTM(64, input_shape=(hist_size, n_features), return_sequences=True))
    model.add(layers.LSTM(32, activation='relu'))
    # model.add(layers.LSTM(16, activation='relu'))
    # model.add(layers.Dense(n_steps_out, activation='linear'))
    model.add(layers.Dense(n_steps_out))
    model.compile(optimizer='adam', loss='mae', metrics=['mean_absolute_error'])

    return model

def cnndnn(input_x, input_y, n_forecast_hours, n_steps_out=1):
    """Define a model architecture that combines CNN and DNN.

    Parameters
    ----------
    input_x : int
        Number of time steps to include in each sample, i.e. how much history
        should be matched with a given target.
    input_y : int
        Number of features for each time step, in the input data.
    dense_x: int
        Number of features for the dense part of the network.
    n_steps_out : int
        Number of output steps.
    Returns
    -------
    model : Keras model
        Model to be trained.
    """
    kernel_size = 4

    input_hist = layers.Input(shape=(input_x, input_y))
    input_forecast = layers.Input(shape=((n_forecast_hours,)))

    c = layers.Conv1D(filters=64, kernel_size=kernel_size,
                            activation='relu', 
                            input_shape=(input_x, input_y))(input_hist)
    c = layers.Conv1D(filters=32, kernel_size=kernel_size,
                            activation="relu")(c)
    c = layers.Flatten()(c)
    c = layers.Dense(128, activation='relu')(c)
    c = models.Model(inputs=input_hist, outputs=c)

    d = layers.Dense(256, input_dim=n_forecast_hours, 
            activation="relu"
    )(input_forecast)
    d = layers.Dense(128, activation="relu")(d)
    d = layers.Dense(64, activation="relu")(d)
    d = models.Model(inputs=input_forecast, outputs=d)

    combined = layers.concatenate([c.output, d.output])

    combined = layers.Dense(256, activation="relu")(combined)
    combined = layers.Dense(128, activation="relu")(combined)
    combined = layers.Dense(64, activation="relu")(combined)
    combined = layers.Dense(n_steps_out, activation="linear")(combined)

    model = models.Model(inputs=[c.input, d.input], outputs=combined)

    model.compile( optimizer='adam', loss='mae')

    return model
