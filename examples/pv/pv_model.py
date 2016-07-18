import pecos.pv
import pvlib
import pandas as pd
import numpy as np

def sapm(pm, poa, wind, temp, sapm_parameters, location):
    sapm_model = pecos.pv.basic_pvlib_performance_model(sapm_parameters, 
                                         location['Latitude'], 
                                         location['Longitude'], 
                                         wind, temp, poa)
    
    # Compute the relative error between observed and predicted DC Power.  
    # Add the composite signal and run a range test
    modeled_dcpower = sapm_model['p_mp']*sapm_parameters['Ns']*sapm_parameters['Np']
    pm.add_signal('Expected DC Power', modeled_dcpower)
    observed_dcpower = pm.df[pm.trans['DC Power']].sum(axis=1)
    dc_power_relative_error = (np.abs(observed_dcpower - modeled_dcpower))/observed_dcpower
    pm.add_signal('DC Power Relative Error', dc_power_relative_error)
    pm.check_range([0,0.1], 'DC Power Relative Error') 
    
    # Compute normalized efficiency, add the composite signal, and run a range test
    P_ref = sapm_parameters['Vmpo']*sapm_parameters['Impo']*sapm_parameters['Ns']*sapm_parameters['Np'] # DC Power rating
    NE = pecos.pv.normalized_efficiency(observed_dcpower, pm.df[pm.trans['POA']], P_ref)
    pm.add_signal('Normalized Efficiency', NE)
    pm.check_range([0.8, 1.2], 'Normalized Efficiency') 
    
    # Compute energy
    energy = pecos.pv.energy(pm.df[pm.trans['AC Power']], tfilter=pm.tfilter)
    total_energy = energy.sum(axis=1)
    
    # Compute insolation
    poa_insolation = pecos.pv.insolation(pm.df[pm.trans['POA']], tfilter=pm.tfilter)
    
    # Compute performance ratio
    PR = pecos.pv.performance_ratio(total_energy, poa_insolation, P_ref)
    
    # Compute performance index
    predicted_energy = pecos.pv.energy(modeled_dcpower, tfilter=pm.tfilter)
    PI = pecos.pv.performance_index(total_energy, predicted_energy)
    
    # Compute clearness index
    dni_insolation = pecos.pv.insolation(pm.df[pm.trans['DNI']], tfilter=pm.tfilter)
    ea = pvlib.irradiance.extraradiation(pm.df.index.dayofyear)
    ea = pd.DataFrame(index=pm.df.index, data=ea, columns=['ea'])
    ea_insolation = pecos.pv.insolation(ea, tfilter=pm.tfilter)
    Kt = pecos.pv.clearness_index(dni_insolation, ea_insolation)
    
    # Compute energy yield
    energy_yield = pecos.pv.energy_yield(total_energy, P_ref)
    
    # Collect metrics for reporting
    total_energy = total_energy/3600/1000 # convert Ws to kWh
    poa_insolation = poa_insolation/3600/1000 # convert Ws to kWh
    energy_yield = energy_yield/3600 # convert s to h
    total_energy = total_energy.to_frame('Total Energy (kWh)')
    poa_insolation.columns = ['POA Insolation (kWh/m2)']
    energy_yield.columns = ['Energy Yield (kWh/kWp)']
    metrics = pd.concat([PR, PI, Kt, total_energy, poa_insolation, energy_yield], axis=1)
    
    return metrics