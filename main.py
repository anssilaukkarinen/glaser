# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 11:35:54 2022

@author: laukkara
"""
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import statsmodels.api as sm

import glaser


fname = os.path.join(r'C:\Local\laukkara\Data\RASMI-datat\2 pickle',
                     'RASMI.pickle')
with open(fname, 'rb') as f:
    data = pickle.load(f)


output_folder = os.path.join(r'C:\Local\laukkara\Data\github\glaser',
                             'output')
if not os.path.exists(output_folder):
    os.makedirs(output_folder)



layers_list_name = 'timber_frame_wall_new'
layers_list = [{'d':0.009,
                'lam': 0.21,
                'mu': 4,
                'evap_layer': True},
                {'d':0.198,
                'lam': 0.037,
                'mu': 1},
                {'R': 0.003,
                'sd': 100.0},
                {'d':0.048,
                'lam': 0.037,
                'mu': 1},
                {'d':0.0125,
                'lam': 0.21,
                'mu': 10}]


# layers_list_name = 'timber_frame_wall_old'
# layers_list = [{'d':0.025,
#                 'lam': 0.13,
#                 'mu': 50,
#                 'evap_layer': True},
#                 {'R': 0.003,
#                 'sd': 0.5},
#                 {'d':0.125,
#                 'lam': 0.06,
#                 'mu': 1.5},
#                 {'R': 0.003,
#                 'sd': 0.5},
#                 {'d':0.025,
#                 'lam': 0.13,
#                 'mu': 50},
#                 {'d':0.01,
#                 'lam': 0.1,
#                 'mu': 50}]


# layers_list_name = 'log_wall_interior_insulation'
# layers_list = [{'d':0.18,
#                 'lam': 0.13,
#                 'mu': 40,
#                 'evap_layer': True},
#                 {'d':0.1,
#                 'lam': 0.039,
#                 'mu': 1},
#                 {'R': 0.003,
#                 'sd': 0.5},
#                 {'d':0.013,
#                 'lam': 0.21,
#                 'mu': 10}]



# layers_list_name = 'concrete_sandwich_panel'
# layers_list = [{'d':0.07,
#                 'lam': 2.3,
#                 'mu': 80,
#                 'evap_layer': True},
#                 {'d':0.25,
#                 'lam': 0.039,
#                 'mu': 1},
#                 {'d':0.15,
#                 'lam': 2.3,
#                 'mu': 130}]




# layers_list_name = 'brick_MW_brick'
# layers_list = [{'d':0.13,
#                 'lam': 0.6,
#                 'mu': 10,
#                 'evap_layer': True},
#                 {'d':0.15,
#                 'lam': 0.04,
#                 'mu': 1},
#                 {'d':0.13,
#                 'lam': 0.6,
#                 'mu': 16}]



#########################################


keys = ['Jok_1989-2018',
        'Jyv_1989-2018',
        'Sod_1989-2018',
        'Van_1989-2018']

# keys = ['Jok_1989-2018']

fname = os.path.join(output_folder,
                     'output_{}.xlsx'.format(layers_list_name))
writer = pd.ExcelWriter(fname)

res = {}

for key in keys:
    
    res[key] = {}
    
    print(key)
    Te_all = data[key].groupby(['YEAR','MON']).mean().loc[(1989,7):(2018,6), 'Te'].values
    RHe_all = data[key].groupby(['YEAR','MON']).mean().loc[(1989,7):(2018,6), 'RHe_ice'].values
    dt_hours = data[key].groupby(['YEAR','MON']).count().loc[:,'Te'].values
    
    # Te_all = data[key].groupby(['YEAR','MON']).mean().loc[:, 'Te'].values
    # RHe_all = data[key].groupby(['YEAR','MON']).mean().loc[:, 'RHe_water'].values
    
    n_years = int(Te_all.shape[0] / 12)
    
    obj_list = []
    mcond_list = []
    mevap_list = []
    RHmaxq100_list = []
    RHmaxq90_list = []
    mpotmaxq100_list = []
    mpotmaxq90_list = []
    
    for idx_year in range(n_years):
        
        Te = Te_all[ (idx_year*12) : ((idx_year+1)*12) ]
        RHe = RHe_all[ (idx_year*12) : ((idx_year+1)*12) ]

        BC = {'Te': Te,
              'RHe': RHe,
              'Ti': 'Ti_const_21',
              'vi': 'RHi_const_50',
              'dt_hours': dt_hours}
        
        obj = glaser.Glaser(layers_list,
                            BC)
        obj_list.append(obj)
        mcond_list.append(obj.mcond)
        mevap_list.append(obj.mevap)
        RHmaxq100_list.append(obj.RHmaxq100)
        RHmaxq90_list.append(obj.RHmaxq90)
        mpotmaxq100_list.append(obj.mpotmaxq100)
        mpotmaxq90_list.append(obj.mpotmaxq90)
    
    res[key]['obj_list'] = obj_list
    
    # version 1: This has all variables
    df = pd.DataFrame(data={'year': np.arange(1989, 1989+n_years,),
                        'mcond': mcond_list,
                        'mevap': mevap_list,
                        'RHmaxq100': RHmaxq100_list,
                        'RHmaxq90': RHmaxq90_list,
                        'mpotmaxq100': mpotmaxq100_list,
                        'mpotmaxq90': mpotmaxq90_list})
    
    # version 2: This has a subset of variables
    # df = pd.DataFrame(data={'year': np.arange(1989, 1989+n_years,),
    #                 'mcond': mcond_list,
    #                 'RHmaxq100': RHmaxq100_list,
    #                 'RHmaxq90': RHmaxq90_list})
    
    
    
    df.index.name = 'index'
    
    res[key]['df'] = df
    
    
    # When there is condensation, relative humidity is 100 % RH and the results saturate
    # Also the mould growth potential saturates towards 100/80 = 1.2
    # If there is condensation, ranked by condensation
    # If there is no condensation, ranked by RHmazq90
    # n_cond = (df['mcond'] > 0).sum()
    # if n_cond > 10:
    #     by_key = 'mcond'
    # else:
    #     by_key = 'RHmaxq90'
    
    df.sort_values(by=['mcond', 'RHmaxq100', 'RHmaxq90'],
                   ascending=False).round(1).to_excel(writer,
                                                        index=False,
                                                        sheet_name=key)

writer.save()



#############################

















