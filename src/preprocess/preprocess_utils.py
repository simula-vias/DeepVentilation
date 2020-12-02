#!/usr/bin/env python3
# ============================================================================
# File:     preprocess_utils
# Author:   Erik Johannes Husom
# Created:  2020-08-26
# ----------------------------------------------------------------------------
# Description:
# Utilities for data preprocessing.
# ============================================================================
import matplotlib.pyplot as plt

# plt.rcParams['figure.figsize'] = [5.0, 3.0]
# plt.rcParams['figure.dpi'] = 300

import datetime
import numpy as np
import os
import pandas as pd
import pickle
import string
import sys
import time
from scipy.fftpack import fft, ifft

from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

from utils import *


def read_csv(filename, delete_columns=[], verbose=False):
    """Read csv file, and make proper adjustment to the resulting dataframe.

    Args:
        filename (str): Name of csv file to read.
        delete_columns (list): Columns to delete. Empty by default.
        verbose (bool): Whether to print info about the file.

    Returns:
        df (DataFrame): Data frame read from file.
        index (Index): Index of data frame read from file.

    """

    # Get input matrix from file
    df = pd.read_csv(filename, index_col=0)

    if verbose:
        print_dataframe(df, "DATAFRAME FROM CSV")

    for col in delete_columns:
        del df[col]

    df.dropna(inplace=True)
    df.reset_index(inplace=True, drop=True)
    index = df.index

    if verbose:
        print("Data file loaded: {}".format(filename))
        print("Length of data set: {}".format(len(df)))

    return df, index


def print_dataframe(df, message=""):
    """Print dataframe to terminal, with boundary and message.

    Args:
        df (DataFrame): Data frame to print.
        message (str): Optional message to print.

    """

    print_horizontal_line()

    print(message)
    print(df)


def move_column(df, column_name, new_idx):
    """
    Move a column in a dataframe.

    Args:
        df (DataFrame): Dataframe containing the column to be moved.
        column_name (str): Name of the column to be moved.
        new_idx (int): The column index the column should be moved to.

    Returns:
        df (DataFrame): Data frame with the columns reordered.

    """

    old_idx = df.columns.get_loc(column_name)
    reordered_columns = list(df.columns)
    reordered_columns.insert(0, reordered_columns.pop(old_idx))

    return df[reordered_columns]


def split_sequences(sequences, hist_size, target_mean_window=1, n_steps_out=1):
    """Split data sequence into samples with matching input and targets.

    Args:
        sequences (array): The matrix containing the sequences, with the
            targets in the first column.
        hist_size (int): Number of time steps to include in each sample, i.e.
            how much history should be matched with a given target.
        target_mean_window (int): Target value will be set as a mean value over
            a window (ending on the current time step) with a size specified
            with this parameter. Default=1, i.e. only one value is used as
            target.
        n_steps_out (int): Number of output steps.

    Returns:
        X (array): The input samples.
        y (array): The targets.

    """
    X, y = list(), list()

    for i in range(len(sequences)):

        # find the end of this pattern
        end_ix = i + hist_size
        out_end_ix = end_ix + n_steps_out

        # find start of target window
        target_start_ix = out_end_ix - target_mean_window

        # check if we are beyond the dataset
        if out_end_ix > len(sequences):
            break
       
        # Select all cols from sequences except target col, which leaves inputs
        seq_x = sequences[i:end_ix, 1:]

        # Extract targets from sequences
        if target_mean_window > 1:
            seq_y = [np.mean(sequences[target_start_ix: out_end_ix, 0])]
        else:
            seq_y = sequences[end_ix:out_end_ix, 0]

        X.append(seq_x)
        y.append(seq_y)

    X = np.array(X)
    y = np.array(y)
    
    return X, y

def flatten_sequentialized(X):
    """Flatten sequentialized data.

    Args:
        X (array): Array of shape [num_sequences, hist_size, num_features].

    Returns:
        X_flat (array): Array of shape [num_sequences, hist_size*num_features].

    """

    X_flat = X.reshape(X.shape[0], X.shape[1]*X.shape[2])

    return X_flat


def merge_time_series_and_added_features(X):
    """
    Reverse the operation done on input matrix X by
    split_time_series_and_added_features, but flattening the time series
    data.

    Parameters
    ----------
    X : list
        This must be a list of two elements:
        1. 2D-array of shape [hist_size, num_features], which contains the time
           series data.
        2. 1D-array of shape [num_added_features], which contains the added
           features.

    Return
    ------
    result : array
        A 2D-array, where each row contains the flattened time series data
        along with the added features, such that each row contains the input
        data needed to make one prediction.

    """

    if isinstance(X, list) and (len(X) == 2):

        result = list()

        for i in range(len(X[0])):
            row = np.concatenate([X[0][i].reshape(-1), X[1][i]])
            result.append(row)

        return np.array(result)

    else:
        raise TypeError("X must be a list of two elements.")


def scale_data(train_data, val_data, scaler_type="minmax"):
    """Scale train and test data.

    Args:
        train_data (array): Train data to be scaled. Used as scale reference
            for test data.
        val_data (array): Test data too be scaled, with train scaling as
            reference.
        scaler_type (str, default='standard'): Options: 'standard, 'minmax'.
            Specifies whether to use sklearn's StandardScaler or MinMaxScaler.

    Returns:
        train_data (array): Scaled train data.
        val_data (array): Scaled test data.
        scaler (scikit-learn scaler): The scaler object that is used.

    """

    if scaler_type == "standard":
        scaler = StandardScaler()
    elif scaler_type == "minmax":
        scaler = MinMaxScaler()
    elif scaler_type == "robust":
        scaler = RobustScaler()
    else:
        raise NotImplementedError(f"{scaler_type} not implemented.")

    train_data = scaler.fit_transform(train_data)
    val_data = scaler.transform(val_data)

    return train_data, val_data, scaler


def split_time_series_and_added_features(X, input_columns, added_features):
    """
    Take the result from split_sequences(), remove weather forecast for all time
    steps (in each sample) except the latest one, and put the latest forecast
    into a separate array. The goal is to have one input matrix for the
    historical observations, which will be given to a CNN, and an array for
    the weather forecast, which will be fed into a dense NN. The networks will
    later be combined. The purpose of this is to remove the outdated forecast
    for each sample, in order to make the input less complex.

    Parameters
    ----------
    X : list/array of arrays
        The input matrix produced by split_sequences().
    input_columns : list of strings
        An array/list that contains the names of the columns in the input
        matrix. This is used to sort out which columns should be a part of the
        historic data, and which data that belongs to the forecast. The sorting
        is done based on that the name of the forecast columns start with a
        digit (the coordinates), while the other columns do not.
    added_features : list
        A list of the features that are added to the raw data. These features
        will not be included in the history window, but will be appended to the
        array of forecast values.

    Returns
    -------
    X_hist : list of arrays
        The input matrix containing historical observations, with the weather
        forecast removed.
    X_forecast : list of arrays
        Input matrix containing the latest weather forecast for each sample.

    """

    X_hist, X_added = list(), list()
    hist_idcs = []
    added_idcs = []

    for i in range(len(input_columns)):
        if input_columns[i] in added_features:
            added_idcs.append(i)
        else:
            hist_idcs.append(i)

    for i in range(len(X)):
        X_hist.append(X[i][:, hist_idcs])
        X_added.append(X[i][-1, added_idcs])

    return [np.array(X_hist), np.array(X_added)]
