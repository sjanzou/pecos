import pecos.pv
import pvlib
import pandas as pd
import numpy as np

def sapm(pm, poa, wind, temp, sapm_parameters, location):
    
    # pvlib expects Pandas series
    if type(wind) is pd.core.frame.DataFrame:
        wind = pd.Series(wind.values[:,0], index=wind.index)
    if type(temp) is pd.core.frame.DataFrame:
        temp = pd.Series(temp.values[:,0], index=temp.index)
    if type(poa) is pd.core.frame.DataFrame:
        poa = pd.Series(poa.values[:,0], index=poa.index)
    poa_diffuse = pd.Series(data=0, index=poa.index)
         
    index = poa.index  
        
    # Copute sun position
    solarposition = pvlib.solarposition.ephemeris(index, location['Latitude'], location['Longitude'])
    
    # Compute cell temperature
    celltemp = pvlib.pvsystem.sapm_celltemp(poa, wind, temp)

    # Compute alsolute airmass
    airmass_relative  = pvlib.atmosphere.relativeairmass(solarposition['zenith'])
    airmass_absolute = pvlib.atmosphere.absoluteairmass(airmass_relative)
    
    # Compute aoi
    aoi = pvlib.irradiance.aoi(location['Latitude'], 180, solarposition['zenith'], solarposition['azimuth'])
           
    Ee = pvlib.pvsystem.sapm_effective_irradiance(poa, poa_diffuse, airmass_absolute, aoi, sapm_parameters)
    sapm_model = pvlib.pvsystem.sapm(Ee, celltemp['temp_cell'], sapm_parameters)
    
    # Compute the relative error between observed and predicted DC Power.  
    # Add the composite signal and run a range test
    modeled_dcpower = sapm_model['p_mp']*sapm_parameters['Ns']*sapm_parameters['Np']
    modeled_dcpower = modeled_dcpower.to_frame('Expected DC Power')
    pm.add_dataframe(modeled_dcpower)
    
    observed_dcpower = pm.df[pm.trans['DC Power']].sum(axis=1)
    dc_power_relative_error = (np.abs(observed_dcpower - pm.df['Expected DC Power']))/observed_dcpower
    dc_power_relative_error = dc_power_relative_error.to_frame('DC Power Relative Error')
    pm.add_dataframe(dc_power_relative_error)
    
    pm.check_range([0,0.1], 'DC Power Relative Error') 
    
    # Compute normalized efficiency, add the composite signal, and run a range test
    P_ref = sapm_parameters['Vmpo']*sapm_parameters['Impo']*sapm_parameters['Ns']*sapm_parameters['Np'] # DC Power rating
    NE = pecos.pv.normalized_efficiency(observed_dcpower, pm.df[pm.trans['POA']], P_ref)
    pm.add_dataframe(NE)
    pm.add_translation_dictionary({'Normalized Efficiency': list(NE.columns)})
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