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


fname = os.path.join(r'C:\Local\laukkara\Data\RASMI-datat\2 pickle',
                     'RASMI.pickle')
with open(fname, 'rb') as f:
    data = pickle.load(f)


output_folder = os.path.join(r'C:\Local\laukkara\Data\github\glaser',
                             'output')
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


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



#########################################




ll_names = [layers_list_name_tfwn,
           layers_list_name_tfwo,
           layers_list_name_lwii,
           layers_list_name_csp,
           layers_list_name_bmwb]

ll_s = [layers_list_tfwn,
           layers_list_tfwo,
           layers_list_lwii,
           layers_list_csp,
           layers_list_bmwb]

Tis = ['Ti_const_21', 'Ti_const_18', 'Ti_ISO13788']

vis = ['RHi_const_50', 'RIL107_2012', 'RHi_ISO13788']


# keys = ['Jok_1989-2018',
#         'Jyv_1989-2018',
#         'Sod_1989-2018',
#         'Van_1989-2018']
keys = data.keys()


for ll_idx in range(len(ll_names)):
    print('ll_idx:', ll_idx)
    
    for Ti in Tis:
        print('Ti:', Ti)
        
        for vi in vis:
            print('vi:', vi)
            
            fname = os.path.join(output_folder,
                                 'output {} {} {}.xlsx'.format(ll_names[ll_idx],
                                                                 Ti,
                                                                 vi))
            writer = pd.ExcelWriter(fname)
            
            res = {}
            
            for key in keys:
                print('key:', key)
                
                res[key] = {}
                
                Te_all = data[key].groupby(['YEAR','MON']).mean().loc[(1989,7):(2018,6), 'Te'].values
                RHe_all = data[key].groupby(['YEAR','MON']).mean().loc[(1989,7):(2018,6), 'RHe_ice'].values
                dt_hours = data[key].groupby(['YEAR','MON']).count().loc[:,'Te'].values
                
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
                          'Ti': Ti,
                          'vi': vi,
                          'dt_hours': dt_hours}
                    
                    obj = glaser.Glaser(ll_s[ll_idx],
                                        BC)
                    obj_list.append(obj)
                    mcond_list.append(obj.mcond)
                    mevap_list.append(obj.mevap)
                    RHmaxq100_list.append(obj.RHmaxq100)
                    RHmaxq90_list.append(obj.RHmaxq90)
                    mpotmaxq100_list.append(obj.mpotmaxq100)
                    mpotmaxq90_list.append(obj.mpotmaxq90)
                
                res[key]['obj_list'] = obj_list
                
                # This has all variables
                df = pd.DataFrame(data={'year': np.arange(1989, 1989+n_years,),
                                    'mcond': mcond_list,
                                    'mevap': mevap_list,
                                    'RHmaxq100': RHmaxq100_list,
                                    'RHmaxq90': RHmaxq90_list,
                                    'mpotmaxq100': mpotmaxq100_list,
                                    'mpotmaxq90': mpotmaxq90_list})
                
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












