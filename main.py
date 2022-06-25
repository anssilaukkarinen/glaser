# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 11:35:54 2022

@author: laukkara

Run first "main.py" and the "analyse_results.py"

"""
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import statsmodels.api as sm

import glaser



input_folder = r'C:\Storage\github\glaser\input' \
               r'\SFS-EN ISO 13788 Kuukausitason laskelmat\csv'


output_folder = r'C:\Storage\github\glaser\output'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)






# Import climate data
converter = {'Jokioinen': 'Jok',
             'Jyväskylä': 'Jyv',
             'Sodankylä': 'Sod',
             'Vantaa': 'Van'}

data = {}
for file in os.listdir(input_folder):
    fname = os.path.join(input_folder,
                         file)
    df = pd.read_csv(fname, sep='\s+')
    key = converter[file.split('_')[0]]
    data[key] = df



# Determine structures

layers_list_name_tfwn = 'timber_frame_wall_new'
layers_list_tfwn = [{'d':0.009,
                'lam': 0.21,
                'mu': 4,
                'evap_layer': True},
                {'d':0.198,
                'lam': 0.033,
                'mu': 1},
                {'R': 0.003,
                'sd': 50.0},
                {'d':0.05,
                'lam': 0.033,
                'mu': 1},
                {'d':0.013,
                'lam': 0.21,
                'mu': 10}]


layers_list_name_tfwo = 'timber_frame_wall_old'
layers_list_tfwo = [{'d':0.02,
                'lam': 0.13,
                'mu': 20,
                'evap_layer': True},
                {'R': 0.003,
                'sd': 0.2},
                {'d':0.125,
                'lam': 0.06,
                'mu': 1.5},
                {'R': 0.003,
                'sd': 0.2},
                {'d':0.02,
                'lam': 0.13,
                'mu': 50},
                {'d':0.012,
                'lam': 0.07,
                'mu': 5}]

layers_list_name_lwii = 'log_wall_interior_insulation'
layers_list_lwii = [{'d':0.18,
                'lam': 0.13,
                'mu': 50,
                'evap_layer': True},
                {'d':0.1,
                'lam': 0.039,
                'mu': 2},
                {'R': 0.003,
                'sd': 0.5},
                {'d':0.013,
                'lam': 0.21,
                'mu': 10}]



layers_list_name_csp = 'concrete_sandwich_panel'
layers_list_csp = [{'d':0.07,
                'lam': 2.3,
                'mu': 80,
                'evap_layer': True},
                {'d':0.22,
                'lam': 0.035,
                'mu': 1},
                {'d':0.08,
                'lam': 2.3,
                'mu': 130}]




layers_list_name_bmwb = 'brick_MW_brick'
layers_list_bmwb = [{'d':0.13,
                'lam': 0.6,
                'mu': 10,
                'evap_layer': True},
                {'d':0.125,
                'lam': 0.041,
                'mu': 1},
                {'d':0.13,
                'lam': 0.6,
                'mu': 16}]



layers_list_names = [layers_list_name_tfwn,
           layers_list_name_tfwo,
           layers_list_name_lwii,
           layers_list_name_csp,
           layers_list_name_bmwb]

layers_list_dicts = [layers_list_tfwn,
                    layers_list_tfwo,
                    layers_list_lwii,
                    layers_list_csp,
                    layers_list_bmwb]


# Indoor air conditions

Tis = ['Ti_const_18'] # ['Ti_const_21', 'Ti_const_18', 'Ti_ISO13788']

vis = ['RIL107_2012'] # ['RHi_const_50', 'RIL107_2012', 'RHi_ISO13788']


res = {}

for idx_ll in range(len(layers_list_names)):
    
    for Ti in Tis:
        
        for vi in vis:
            
            for key in data.keys():
                
                
                BC = {'Te': data[key].loc[:, 'Te'].values,
                      'RHe': data[key].loc[:, 'RHe'].values,
                      'Ti': Ti,
                      'vi': vi,
                      'dt_hours': data[key].loc[:, 'dt'].values}
                
                obj = glaser.Glaser(layers_list_dicts[idx_ll],
                                    BC,
                                    2)
                
                
                res_key = '{}_{}_{}_{}'.format(layers_list_names[idx_ll],
                                                Ti,
                                                vi,
                                                key)
                
                res[res_key] = obj















