"""
The pv module contains custom methods for PV applications.
"""
import pandas as pd
import numpy as np
import datetime 
from pecos.metrics import time_integral
import logging

logger = logging.getLogger(__name__)

def insolation(irradiance, time_unit=1, tfilter=None, per_day=True):
    """
    Convert irradiance to insolation by taking the time integral.
    Results are given in [irradiance units]*seconds.
    
     Parameters
    -----------
    irradiance : pd.DataFrame
        Irradiance
        
    time_unit : float (default = 1)
         Convert time unit of integration.  time_unit = 3600 returns integral in units of hours.
         
    tfilter : pd.Series (default = None)
        Time filter containing boolean values for each time index
        
    per_day : Boolean (default = True)
        Flag indicating if the results should be computed per day
    
    Returns
    -------
    insolation : pd.DataFrame
        Insolation
    """
    insolation = time_integral(irradiance, time_unit=time_unit, tfilter=tfilter, per_day=per_day)
    
    return insolation
    
def energy(power, time_unit=1, tfilter=None, per_day=True):
    """
    Convert power to energy by taking the time integral.
    Results are given in [power units]*seconds.
    
    Parameters
    -----------
    power : pd.DataFrame
        Power
        
    time_unit : float (default = 1)
         Convert time unit of integration.  time_unit = 3600 returns integral in units of hours.
         
    tfilter : pd.Series (default = None)
        Time filter containing boolean values for each time index
        
    per_day : Boolean (default = True)
        Flag indicating if the results should be computed per day
    
    Returns
    -------
    energy : pd.DataFrame
        Energy
    """
    energy = time_integral(power, time_unit=time_unit, tfilter=tfilter, per_day=per_day)
    
    return energy
    
def performance_ratio(energy, insolation, dc_power_rating, reference_irradiance=1000):
    """
    Compute performance ratio defined as:

    :math:`PR=\dfrac{Y_{f}}{Yr}`
    
    where 
    :math:`Y_f` is the the measured energy (AC or DC) produced by the PV system (kWh) 
    divided by the rated power of the PV system.  The rated power is the DC power rating 
    at STC conditions (1000 W/m2, cell temperature of 25 C, and AM1.5 spectrum).
    :math:`Y_r` is the plane-of-array insolation (kWh/m2) divided 
    by the reference irradiance (1000 W/m2).  :math:`Y_r` is in units of time.
    
    Parameters
    -----------
    energy : pd.DataFrame with a single column or pd.Series
        Energy (AC or DC)
        
    insolation : pd.DataFrame with a single column or pd.Series
         Plane of array insolation
         
    dc_power_rating : float
        DC power rating at STC conditions
        
    reference_irradiance : float (default = 1000)
        Reference irradiance
        
    Returns
    -------
    PR : pd.DataFrame
        Performance ratio
    """
    logger.info("Compute Performance Ratio")
    
    try:
        energy = pd.Series(energy, index=energy.index)
    except:
        logger.info('Cannot convert energy to pd.Series')
        return

    try:
        insolation = pd.Series(insolation, index=insolation.index)
    except:
        logger.info('Cannot convert insolation to pd.Series')
        return
        
    Yf = energy/dc_power_rating
    Yr = insolation/reference_irradiance
    PR = Yf/Yr
    
    PR = PR.to_frame('Performance Ratio')
    
    return PR
    
def performance_index(energy, predicted_energy):
    """
    Compute performance index defined as the ratio of measured energy from a PV system 
    to the predicted energy using a PV performance model.  Unlike with the 
    performance ratio, the performance index very close to 1 for a well 
    functioning PV system and should not vary by season due to temperature 
    variations.
    
    Parameters
    -----------
    energy : pd.DataFrame with a single column or pd.Series
        Measured energy
    
    predicted_energy: pd.DataFrame with a single column or pd.Series
        Predicted energy
        
    Returns
    ---------
    PI : pd.DataFrame
        Performance index 
    """
    logger.info("Compute Performance Index")
    
    try:
        energy = pd.Series(energy, index=energy.index)
    except:
        logger.info('Cannot convert energy to pd.Series')
        return

    try:
        predicted_energy = pd.Series(predicted_energy, index=predicted_energy.index)
    except:
        logger.info('Cannot convert predicted_energy to pd.Series')
        return
        
    PI = energy/predicted_energy
    
    PI = PI.to_frame('Performance Index')
    
    return PI

def energy_yield(energy, dc_power_rating):
    """
    Compute energy yield defined as the energy produced over a given timeframe 
    divided by the DC power rating of the system.
    
    Parameters
    -----------
    energy : pd.DataFrame with a single column or pd.Series
        Measured energy
    
    dc_power_rating : float
        DC power rating at STC conditions
        
    Returns
    ---------
    EY : pd.DataFrame
        Energy yield  
    """
    logger.info("Compute Energy Yield")
    
    try:
        energy = pd.Series(energy, index=energy.index)
    except:
        logger.info('Cannot convert energy to pd.Series')
        return

    EY = energy/dc_power_rating
    
    EY = EY.to_frame('Energy Yield')
    
    return EY
    
def clearness_index(dni_insolation, ea_insolation):
    """
    Compute clearness index defined as:
    
    :math:`Kt=\dfrac{DN\_insolation}{Ex\_insolation}`
    
    where 
    :math:`DN\_insolation` is the direct-normal insolation in one day 
    (kWh/m2/d)
    :math:`Ex\_insolation` is the extraterrestrial insolation in one 
    day (kWh/m2/d).  Computed using pvlib.irradiance.extraradiation.
    
    Parameters
    -----------
    insolation : pd.DataFrame with a single column or pd.Series
        Direct normal insolation
        
    Returns
    -------
    Kt : Pandas DataFrame or float
        Clearness index
    """
    try:
        dni_insolation = pd.Series(dni_insolation, index=dni_insolation.index)
    except:
        logger.info('Cannot convert dni_insolation to pd.Series')
        return

    try:
        ea_insolation = pd.Series(ea_insolation, index=ea_insolation.index)
    except:
        logger.info('Cannot convert ea_insolation to pd.Series')
        return
        
    Kt = dni_insolation/ea_insolation
        
    Kt = Kt.to_frame('Clearness Index')
    
    return Kt
