# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 11:35:54 2022

@author: laukkara
"""
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt

import glaser

## puurankaseinä
# layers_list = [{'d':0.009,
#                 'lam': 0.21,
#                 'mu': 4},
#                 {'d':0.25,
#                 'lam': 0.039,
#                 'mu': 1},
#                 {'R': 0.001,
#                 'sd': 0.0005},
#                 {'d':0.0125,
#                 'lam': 0.21,
#                 'mu': 10}]

## betonisandwich
layers_list = [{'d':0.07,
                'lam': 2.3,
                'mu': 80},
                {'d':0.25,
                'lam': 0.039,
                'mu': 60},
                {'d':0.15,
                'lam': 2.3,
                'mu': 130}]

BC = {'Te': 0.0,
      'RHe': 90.0,
      'Ti': 17.0,
      'dv': 'RIL107_2012'}

RHmin = 85.0

obj = glaser.Glaser(layers_list,
                    BC,
                    RHmin)

obj.plot_basics()