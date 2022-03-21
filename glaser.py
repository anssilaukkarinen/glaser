# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 11:19:02 2022

@author: laukkara
"""

import numpy as np
import matplotlib.pyplot as plt


class Glaser():
    
    def __init__(self, layers_list_input, BC_dict_input):
        
        ## constants
        # Surface resistances
        self.Rse = 0.13
        self.Rsi = 0.13
        self.sdse = 0.0
        self.sdsi = 0.0
        
        self.dsurf = 0.05
        self.R_layer_max = 0.05
        
        self.delta_v_air = 0.000025
        
        
        ## initialisations
        # check that layers have R <= 0.2 m2K/W
        self.layers_list_input = layers_list_input
        self.prepare_layers()
        
        
        # Calculate indoor and outdoor vapor concentrations for each time step
        self.Te = BC_dict_input['Te']
        self.RHe = BC_dict_input['RHe']
        self.ve = (self.RHe/100.0) * self.calc_vsat(self.Te)
        
        self.Ti = self.calc_Ti(BC_dict_input['Ti'])
        self.vi = self.calc_vi(BC_dict_input['vi'])
        
        self.dT_tot = self.Ti - self.Te
        self.dv_tot = self.vi - self.ve
        
        self.dt_hours = BC_dict_input['dt_hours']
        
        
        
        ## calculations
        
        self.main()
        

        
        
        
    
    @staticmethod
    def calc_vsat(T):
        # SFS-EN ISO 13788
        # [T] = degC
        # vsat is calculated over ice in subzero temperatures
        if type(T) == np.float64:
            T = np.array([T])
        
        vsat = np.zeros(T.shape)
        for idx_Tval, Tval in enumerate(T):
            if Tval >= 0.0:
                # water
                pvsat = 610.5 * np.exp((17.269*Tval)/(237.3+Tval))
                vsat[idx_Tval] = pvsat/(462.0*(273.15+Tval))
            else:
                # ice
                pvsat = 610.5 * np.exp((21.875*Tval)/(265.5+Tval))
                vsat[idx_Tval] = pvsat/(462.0*(273.15+Tval))
        
        return(vsat)
    
    
    @staticmethod
    def calc_dv(Te):
        dv = []
        for Te_val in Te:
            if Te < 5.0:
                dv.append(0.005)
            elif Te > 15.0:
                dv.append(0.002)
            else:
                dv.append((6.5 - 0.3*Te) / 1000.0)
        dv = np.array(dv)
        return(dv)
    
    
    @staticmethod
    def RH_crit(T):
        RHmin = 80.0
        
        RHcrit = np.zeros(len(T))
        
        for idx_Tval, Tval in enumerate(T):
            if Tval < 0.0:
                RHcrit[idx_Tval] = 100.0
            
            elif Tval <= 20.0:
                dummy = -0.00267*Tval**3 \
                        +0.160*Tval**2 \
                        -3.13*Tval \
                        +100.0
                RHcrit[idx_Tval] = np.max((dummy, RHmin))
            
            elif Tval <= 50.0:
                RHcrit[idx_Tval] = RHmin
            
            else:
                RHcrit[idx_Tval] = 100.0
        
        return(RHcrit)
        


    

    def prepare_layers(self):
        
        self.layers_list_d = []
        self.layers_list_R = []
        self.layers_list_sd = []
        
        self.interface_idxs = []
        
        for idx_layer, layer in enumerate(self.layers_list_input):
            
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
            
            n = 50
            
            # create a list of resistances
            for idx in range(n):
                self.layers_list_d.append(d/n)
                self.layers_list_R.append((d/n) / lam)
                self.layers_list_sd.append((d/n) * mu)
            
            # create a list of interface indexis for mould growth risk calculation
            # the last round is for interior surface, which is included
            self.interface_idxs.append(1 + (idx_layer+1) * n)
            
            # determine single interface index for evaporation calculation
            if 'evap_layer' in layer.keys():
                self.idx_evap_layer = 1 + len(self.layers_list_d)
            
        
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
        
        self.R_tot = self.R_cum[-1]
        self.sd_tot = self.sd_cum[-1]


    def calc_Ti(self, arg1):
        if arg1 == 'Ti_const_21':
            Ti = 21.0 * np.ones(self.Te.shape)
        
        elif arg1 == 'Ti_const_18':
            Ti = 18.0 * np.ones(self.Te.shape)
            
        else:
            print('Unknown Ti arg1')
            Ti = np.nan
        return(Ti)
    
    

    def calc_vi(self, arg1):
        if arg1 == 'RIL107_2012':
            vi = self.ve + self.calc_dv(self.Te)
        elif arg1 == 'RHi_const_50':
            vi = (50.0/100.0) * self.calc_vsat( self.Ti )
        else:
            print('Unknown arg1!')
            vi = np.nan
        return(vi)


    @staticmethod
    def func_list_condensation_ranges(RHx):
        # This function counts the number of condensation regions
        # inside the structure
        
        local_variable_list_condensation_ranges = []
        counter = 0
        
        while counter < len(RHx):
            
            if RHx[counter] > 100.0:
                # condensation range starts
                
                idx_exterior = counter
                idx_interior = counter
                
                counter = counter + 1
                
                while counter < len(RHx) and RHx[counter] > 100.0:
                    idx_interior = counter
                    
                    counter = counter + 1
                
                # The condensation range has ended
                condensation_range = {'exterior': idx_exterior,
                                      'interior': idx_interior}
                local_variable_list_condensation_ranges.append(condensation_range)
                # print('cond range', condensation_range)
                
            counter = counter + 1
        
        return(local_variable_list_condensation_ranges)






    def main(self):
        
        self.gcond = np.zeros(self.Te.shape)
        self.gevap = np.zeros(self.Te.shape)
        self.RHmax = np.zeros(self.Te.shape)
        self.mpotmax = np.zeros(self.Te.shape)
        
        for idx, Te_val in enumerate(self.Te):
            
            Te = self.Te[idx]
            ve = self.ve[idx]
            Ti = self.Ti[idx]
            vi = self.vi[idx]
            dt = self.dt_hours[idx] * 3600.0
            
            dT_tot = Ti - Te
            dv_tot = vi - ve
            
            # Temperature and saturation concentration
            Tn = Te + (self.R_cum/self.R_cum[-1]) * dT_tot
            vsatn = self.calc_vsat(Tn)
            
            ## Vapor concentration and relative humidity
            # Round 1
            vn = ve + (self.sd_cum/self.sd_cum[-1]) * dv_tot
            phin = 100.0 * (vn / vsatn)
            # print(idx, self.Te[idx].round(1),
            #           self.RHe[idx].round(1),
            #           phin.max().round(1))
            
            
            
            # Go through relative humidity values and see, if there is condensation
            list_condensation_ranges = self.func_list_condensation_ranges(phin)
            
            n_cond_ranges = len(list_condensation_ranges)            
            
            ##
            if n_cond_ranges == 0:
                
                # amount of condensation (no condensation)
                self.gcond[idx] = 0.0
                
                # amount of evaporation
                T_evap = Tn[self.idx_evap_layer]
                v_sat_evap = self.calc_vsat(T_evap)

                dv_interior = vi - v_sat_evap
                sd_interior = self.sd_cum[-1] - self.sd_cum[self.idx_evap_layer]
                g_in = self.delta_v_air * (dv_interior / sd_interior)
                
                dv_exterior = v_sat_evap - ve
                sd_exterior = self.sd_cum[self.idx_evap_layer]
                g_out = self.delta_v_air * (dv_exterior / sd_exterior)
                
                self.gevap[idx] = (g_in - g_out) * dt * 1000.0
                # print('gevap = ', self.gevap[idx].round(1), 'g/m2')
                
                
                # maximum relative humidity
                self.RHmax[idx] = phin[self.interface_idxs].max()
                
                
                # mould growth potential at material interfaces
                T_M = Tn[self.interface_idxs]
                phi_M = phin[self.interface_idxs]
                phi_M_min = self.RH_crit(T_M)
                
                m_pot = phi_M / phi_M_min
                # print(m_pot.round(2))
                self.mpotmax[idx] = m_pot.max()
                
                
                
            
            
            elif n_cond_ranges == 1:                
                # There is only one condensation range in the structure

                # amount of condensation
                idxs_phi_high = phin > 100.0
                idx_exterior_border = idxs_phi_high.argmax()
                idx_interior_border = (idxs_phi_high.shape[0] - 1) - idxs_phi_high[::-1].argmax()
                
                v_exterior_border = self.calc_vsat(Tn[idx_exterior_border])
                v_interior_border = self.calc_vsat(Tn[idx_interior_border])
                
                dv_exterior = v_exterior_border - ve
                sd_exterior = self.sd_cum[idx_exterior_border]
                g_out = self.delta_v_air * (dv_exterior / sd_exterior)
                
                dv_interior = vi - v_interior_border
                sd_interior = self.sd_cum[-1] - self.sd_cum[idx_interior_border]
                g_in = self.delta_v_air * (dv_interior / sd_interior)
                
                self.gcond[idx] = (g_in - g_out) * dt * 1000.0
                
                # amount of evaporation
                self.gevap[idx] = 0.0
                #print('g_cond_net =', self.gcond[idx].round(1), 'g/m2')
                
                
                # update vapor concentration
                # condensation region
                vn_limited = vn.copy()
                vn_limited[idx_exterior_border:idx_interior_border] \
                    = vn[idx_exterior_border:idx_interior_border]
                
                # exterior side
                sd_vals = self.sd_cum[:idx_exterior_border]
                vn_limited[:idx_exterior_border] \
                    = ve + (sd_vals/sd_vals[-1]) * dv_exterior
                
                # interior side
                sd_vals = self.sd_cum[idx_interior_border:] - self.sd_cum[idx_interior_border]
                vn_limited[idx_interior_border:] \
                    = v_interior_border + (sd_vals/sd_vals[-1]) * dv_interior
                
                
                # relative humidity
                phin_limited = vn_limited / vsatn
                self.RHmax[idx] = phin_limited[self.interface_idxs].max()
                
                                
                # mould growth potential at material interfaces                
                T_M = Tn[self.interface_idxs]
                phi_M = phin_limited[self.interface_idxs]
                phi_M_min = self.RH_crit(T_M)
                
                m_pot = phi_M / phi_M_min
                # print(m_pot.round(2))
                self.mpotmax[idx] = m_pot.max()
                
            
            else:
                print('number of condensation ranges per structure:', n_cond_ranges)

                
                
        self.mcond = self.gcond.sum()
        self.mevap = self.gevap.sum()
        self.RHmaxq100 = np.quantile(self.RHmax, 1.0)
        self.RHmaxq90 = np.quantile(self.RHmax, 0.9)
        self.mpotmaxq100 = np.quantile(self.mpotmax, 1.0)
        self.mpotmaxq90 = np.quantile(self.mpotmax, 0.9)
    


        
    def print_info(self):
        
        print('Rtot =', self.R_cum[-1].round(2),
              'U =', np.round(1/self.R_cum[-1], 3),
              'sdtot =', self.sd_cum[-1].round(2))
        
        

    
    
    
    
    
    
    