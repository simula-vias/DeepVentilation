#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visualize data.

Author:   
    Erik Johannes Husom

Created:  
    2020-09-30

"""
import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from preprocess_utils import read_csv, move_column

def visualize(stage="restructured"):
    """Visualize data set.

    Args:
        stage (str): Which stage of the data to plot. Options:
            - restructured
            - featurized

    """

    data_dir = "assets/data/" + stage + "/"

    filepaths = os.listdir(data_dir)

    for filepath in filepaths:

        filepath = data_dir + filepath

        # Read csv, and delete specified columns
        df = pd.read_csv(filepath, index_col=0)

        df.plot()
        plt.title(filepath)
        plt.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Visualize data set")

    parser.add_argument("-r", "--restructured", help="Plot restructured data.",
            action="store_true")
    parser.add_argument("-f", "--featurized", help="Plot featurized data.",
            action="store_true")

    args = parser.parse_args()

    if args.restructured:
        visualize("restructured")

    if args.featurized:
        visualize("featurized")
