#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Combines workout files into one.

Author:   
    Erik Johannes Husom

Created:  
    2020-10-29

"""
import sys

import numpy as np

from config import DATA_COMBINED_PATH

def combine(filepaths):
    """Combine data from multiple workouts into one dataset.

    Args:
        filepaths (list of str): A list of paths to files containing
            sequentialized data.

    """

    DATA_COMBINED_PATH.mkdir(parents=True, exist_ok=True)

    # If filepaths is a string (e.g. only one filepath), wrap this in a list
    if isinstance(filepaths, str):
        filepaths = [filepaths]

    train_inputs = []
    train_outputs = []
    test_inputs = []
    test_outputs = []

    for filepath in filepaths:
        infile = np.load(filepath)
        
        if "train" in filepath:
            train_inputs.append(infile["X"])
            train_outputs.append(infile["y"])
        elif "test" in filepath:
            test_inputs.append(infile["X"])
            test_outputs.append(infile["y"])

    X_train = np.concatenate(train_inputs)
    y_train = np.concatenate(train_outputs)
    X_test = np.concatenate(test_inputs)
    y_test = np.concatenate(test_outputs)

    np.savez(DATA_COMBINED_PATH / "train.npz", X=X_train, y=y_train)
    np.savez(DATA_COMBINED_PATH / "test.npz", X=X_test, y=y_test)

if __name__ == "__main__":

    np.random.seed(2020)

    combine(sys.argv[1:])
