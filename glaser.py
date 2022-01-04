# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 11:19:02 2022

@author: laukkara
"""

import numpy as np
import matplotlib.pyplot as plt


class Glaser():
    
    def __init__(self, layers_list_input, BC_dict_input, RHmin_input):
        
        ## constants
        # Surface resistances
        self.Rse = 0.04
        self.Rsi = 0.13
        self.sdse = 0.0
        self.sdsi = 0.0
        
        self.dsurf = 0.05
        self.R_layer_max = 0.05
        
        
        ## initialisations
        # check that layers have R <= 0.2 m2K/W
        self.layers_list_input = layers_list_input
        self.prepare_layers()
        
        # Calculate indoor and outdoor vapor concentration
        self.Te = BC_dict_input['Te']
        self.RHe = BC_dict_input['RHe']
        self.ve = (self.RHe/100.0) * self.calc_vsat(self.Te)
        
        self.Ti = BC_dict_input['Ti']
        self.vi = self.ve + self.calc_dv(self.Te)
        
        self.dT_tot = self.Ti - self.Te
        self.dv_tot = self.vi - self.ve
        
        # Mould growth potential calculations
        self.RHmin = RHmin_input
        
        
        ## calculations
        self.calc_Tn_vsat()
        
        self.calc_vn_phi()
        
        self.calc_M_potential()
        
        
        
    
    @staticmethod
    def calc_vsat(T):
        # [T] = degC
        pvsat = 610.5 * np.exp((17.269*T)/(237.3+T))
        vsat = pvsat/(462.0*(273.15+T))
        return(vsat)
    
    
    @staticmethod
    def calc_dv(Te):
        if Te < 5.0:
            dv = 0.005
        elif Te > 15.0:
            dv = 0.002
        else:
            dv = (6.5 - 0.3*Te) / 1000.0
    
        return(dv)
    
    
    @staticmethod
    def RH_crit(T, RHmin):
        
        RHcrit = np.zeros(len(T))
        
        for idx_Tval, Tval in enumerate(T):
            if Tval < 0.0:
                RHcrit[idx_Tval] = 100.0
            
            elif Tval <= 20.0:
                RHcrit[idx_Tval] = -0.00267*Tval**3 \
                                   + 0.160*Tval**2 \
                                   -3.13*Tval \
                                   +100.0
            else:
                RHcrit[idx_Tval] = RHmin
        
        return(RHcrit)
        
    
    



    def prepare_layers(self):
        
        self.layers_list_d = []
        self.layers_list_R = []
        self.layers_list_sd = []
        
        for layer in self.layers_list_input:
            
            if 'd' in layer.keys():
                d = layer['d']
                lam = layer['lam']
                mu = layer['mu']
                R = d/lam
            
            else:
                d = 0.001
                R = layer['R']
                lam = d / R
                mu = layer['sd'] / d
            
            # divide into shorter distances, if necessary
            if R <= self.R_layer_max:
                self.layers_list_d.append(d)
                self.layers_list_R.append(d / lam)
                self.layers_list_sd.append(d * mu)
            else:
                n = np.ceil(R/self.R_layer_max).astype(int)
                for idx in range(n):
                    
                    self.layers_list_d.append(d/n)
                    self.layers_list_R.append((d/n) / lam)
                    self.layers_list_sd.append((d/n) * mu)
            
        # add surface resistances
        self.layers_list_d.insert(0, self.dsurf)
        self.layers_list_R.insert(0, self.Rse)
        self.layers_list_sd.insert(0, self.sdse)
        
        self.layers_list_d.append(self.dsurf)
        self.layers_list_R.append(self.Rsi)
        self.layers_list_sd.append(self.sdsi)
            
        # calculate cumulative sums
        np_zero_array = np.array([0])
        
        self.d_cum = np.concatenate( (np_zero_array,
                                      np.cumsum( self.layers_list_d )) )
        
        self.R_cum = np.concatenate( (np_zero_array,
                                      np.cumsum( self.layers_list_R )) )
        
        self.sd_cum = np.concatenate( (np_zero_array,
                                       np.cumsum( self.layers_list_sd )) )
        
        print('Rtot =', self.R_cum[-1].round(2),
              'U =', np.round(1/self.R_cum[-1], 3),
              'sdtot =', self.sd_cum[-1].round(2))
        
    
    def calc_Tn_vsat(self):
        
        self.Tn = self.Te \
            + (self.R_cum /self.R_cum[-1]) * self.dT_tot
        
        self.vsatn = self.calc_vsat(self.Tn)
        
    
    def calc_vn_phi(self):
        
        self.vn = self.ve \
            + (self.sd_cum / self.sd_cum[-1]) * self.dv_tot
        
        self.phin = 100.0 * (self.vn / self.vsatn)
    
    

    def calc_M_potential(self):
        
        self.Mpotn = self.phin / self.RH_crit(self.Tn, self.RHmin)
        
        
        
        
    
    def plot_basics(self):
        
        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(self.d_cum, self.Tn, '-o')
        ax.grid(True)
        ax.set_xlabel('Etäisyys ulkopinnasta, m')
        ax.set_ylabel('Tn, C')
        
        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(self.d_cum, self.vsatn, '-o')
        ax.plot(self.d_cum, self.vn, '-s')
        ax.grid(True)
        ax.set_xlabel('Etäisyys ulkopinnasta, m')
        ax.set_ylabel('v, kg/m3')
        ax.legend(['vsat', 'v'])
    
        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(self.d_cum, self.phin, '-o')
        ax.grid(True)
        ax.set_xlabel('Etäisyys ulkopinnasta, m')
        ax.set_ylabel('phin, %')
    
        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(self.d_cum, self.phin/self.RH_crit(self.Tn, self.RHmin), '-o')
        ax.grid(True)
        ax.set_xlabel('Etäisyys ulkopinnasta, m')
        ax.set_ylabel('Mpot, -')
    
    
    
    
    
    
    
    
    
    
    
    
    