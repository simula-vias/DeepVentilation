#!/usr/bin/env python3
"""Split data into training and test set.

Author:
    Erik Johannes Husom

Date:
    2020-10-29

"""
import os
import sys

import numpy as np
import yaml

from config import DATA_SPLIT_PATH
# from config import DATA_SPLIT_TRAIN_PATH, DATA_SPLIT_TEST_PATH
from preprocess_utils import read_csv

def split(filepaths):
    """Split data into train and test set.

    Training files and test files are saved to different folders.

    Args:
        filepaths (list of str): A list of paths to files containing
            featurized data.

    """

    # Handle special case where there is only one workout file.
    if isinstance(filepaths, str) or len(filepaths) == 1:
        raise NotImplementedError("Cannot handle only one workout file.")

    DATA_SPLIT_PATH.mkdir(parents=True, exist_ok=True)
    # DATA_SPLIT_TRAIN_PATH.mkdir(parents=True, exist_ok=True)
    # DATA_SPLIT_TEST_PATH.mkdir(parents=True, exist_ok=True)

    params = yaml.safe_load(open("params.yaml"))["split"]

    # Parameter 'train_split' is used to find out no. of files in training set
    file_split = int(len(filepaths) * params["train_split"])

    training_files = filepaths[:file_split]
    test_files = filepaths[file_split:]

    for filepath in filepaths:

        df, index = read_csv(filepath)

        if filepath in training_files:
            df.to_csv(
                DATA_SPLIT_PATH
                / (os.path.basename(filepath).replace("featurized", "train"))
            )
        elif filepath in test_files:
            df.to_csv(
                DATA_SPLIT_PATH
                / (os.path.basename(filepath).replace("featurized", "test"))
            )

if __name__ == "__main__":

    np.random.seed(2020)

    split(sys.argv[1:])
