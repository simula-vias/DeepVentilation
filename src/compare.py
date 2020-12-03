#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-liner describing module.

Longer description.

Example:

    >>>

Attributes:


TODO:


Author:   
    Erik Johannes Husom

Created:  
    2020-09-18

"""


import numpy as np
import matplotlib.pyplot as plt

X_app = np.load("X_app.npy")
X_model = np.load("X_model.npy")

print(X_app.shape)
print(X_model.shape)

plt.plot(X_app[0])
plt.plot(X_model[0], "r--")
plt.show()
