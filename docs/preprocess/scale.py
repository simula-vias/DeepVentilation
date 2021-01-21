#!/usr/bin/env python3
"""Scaling the inputs of the data set.

Possible scaling methods

TODO:
    Implement scaling when there is only one workout file.

Author:   
    Erik Johannes Husom

Created:  
    2020-09-16

"""
import os
import sys

import joblib 
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import yaml

from config import DATA_SCALED_PATH
from preprocess_utils import read_csv, scale_data

def scale(filepaths):
    """Scale training and test data.

    Args:
        filepaths (list): List of files to scale. Files need to be have either
            'train' or 'test' in the name to be recognized.

    """

    # If filepaths is a string (e.g. only one filepath), wrap this in a list
    if isinstance(filepaths, str):
        filepaths = [filepaths]

    DATA_SCALED_PATH.mkdir(parents=True, exist_ok=True)

    params = yaml.safe_load(open("params.yaml"))["scale"]
    method = params["method"]
    
    if method == "standard":
        scaler = StandardScaler()
    elif method == "minmax":
        scaler = MinMaxScaler()
    elif method == "robust":
        scaler = RobustScaler()
    else:
        raise NotImplementedError(f"{scaler_type} not implemented.")

    train_inputs = []

    data_overview = {}

    for filepath in filepaths:

        df, index = read_csv(filepath)
        
        # Convert to numpy
        data = df.to_numpy()

        # Split into input (X) and output/target (y)
        X = data[:, 1:].copy()
        y = data[:, 0].copy().reshape(-1, 1)


        if "train" in filepath:
            train_inputs.append(X)
            category = "train"
        elif "test" in filepath:
            category = "test"
            
        data_overview[filepath] = {"X": X, "y": y, "category": category}

    X_train = np.concatenate(train_inputs)

    # Fit a scaler to the training data
    scaler = scaler.fit(X_train)
    joblib.dump(scaler, DATA_SCALED_PATH / "scaler.sav")

    for filepath in data_overview:

        # Scale inputs
        X = scaler.transform(data_overview[filepath]["X"])

        # Save X and y into a binary file
        np.savez(
            DATA_SCALED_PATH
            / (
                os.path.basename(filepath).replace(
                    data_overview[filepath]["category"] + ".csv", 
                    data_overview[filepath]["category"] + "-scaled.npz"
                )
            ),
            X=data_overview[filepath]["X"],
            y=data_overview[filepath]["y"]
        )


if __name__ == "__main__":

    np.random.seed(2020)

    scale(sys.argv[1:])
