"""
The pv module contains custom methods for PV applications.
"""
import pandas as pd
import numpy as np
import datetime 
import logging

logger = logging.getLogger(__name__)

def ac_performance_ratio(acpower, poa, DC_power_rating, tfilter=None, per_day=True):
    """
    The daily AC performance ratio (:math:`PR_{AC}`) is defined in IEC 61724 as:

    :math:`PR_{AC}=\dfrac{Y_{fAC}}{Yr}`
    
    where 
    :math:`Y_fAC` is ths the AC system yield defined as the measured AC energy 
    produced by the PV system in the day (kWh/d) divided by 
    the rated power of the PV system.  The definition of this rating is not 
    specified in IEC 61724, but is defined here as DC power rating at 
    STC conditions (1000 W/m2, cell temperature of 25 C, and AM1.5 spectrum).
    :math:`Y_r` is the plane-of-array insolation (kWh/m2) divided 
    by the reference irradiance (1000 W/m2).  :math:`Y_r` is in units of time.
    
    Parameters
    -----------
    acpower : Pandas DataFrame
        AC power
        
    poa : Pandas DataFrame
         Plane of array irradiance
         
    DC_power_rating : float
        DC power rating at STC conditions
        
    tfilter : Pandas Series (default = None)
        Time filter containing boolean values for each time index
        
    per_day : Boolean (default = True)
        Flag indicating if the results shoudl be computed per day
        
    Returns
    -------
    PR_AC : Pandas DataFrame or float
        AC performance ratio, if per_day = True, then a dataframe indexed by day 
        is returned, otherwise a single vlaue is returned for the entire dataset.
    """
    logger.info("Compute AC Performance Ratio")
    
    # Combine ac power and poa into a single dataframe
    df = acpower.join(poa)
    df = df[~df.isnull().any(axis=1)] # remove any data where is null
    trans = {'acpower': acpower.columns, 'poa': poa.columns}
    
    # Remove time filter
    if tfilter is not None:
        df = df[tfilter]
    
    if per_day:
        dates = [df.index[0].date() + datetime.timedelta(days=x) for x in range(0, (df.index[-1].date()-df.index[0].date()).days+1)]
      
        PR_AC = pd.DataFrame(index=pd.to_datetime(dates))
        
        for date in dates:
            df_date = df.loc[date.strftime('%m/%d/%Y')] 
            try:
                acpower = df_date[trans['acpower']] # W
                poa = df_date[trans['poa']] # W/m2
                ACEnergy = np.sum(np.sum(acpower, axis=1), axis=0) # W[T]/d
                POAInsolation = np.sum(poa, axis=0) #W[T]/m2/d
                ReferenceIrradiance = 1000 # W/m2
                YfAC = np.divide(ACEnergy,DC_power_rating)
                Yr = np.divide(POAInsolation,ReferenceIrradiance)
                PR_AC.loc[date, 'Performance Ratio'] = float(np.divide(YfAC,Yr))
            except:
                PR_AC.loc[date, 'Performance Ratio'] = 'NaN'
    else:
        acpower = df[trans['acpowerr']] # W
        poa = df[trans['poa']] # W/m2
        ACEnergy = np.sum(np.sum(acpower, axis=1), axis=0) # W[T]/d
        POAInsolation = np.sum(poa, axis=0) #W[T]/m2/d
        ReferenceIrradiance = 1000 # W/m2
        YfAC = np.divide(ACEnergy,DC_power_rating)
        Yr = np.divide(POAInsolation,ReferenceIrradiance)
        PR_AC = np.divide(YfAC,Yr)
        
    return PR_AC
    
def clearness_index(dni, tfilter=None, per_day=True):
    """
    Clearness index (:math:`Kt`) is defined as:
    
    :math:`Kt=\dfrac{DN\_insolation}{Ex\_insolation}`
    
    where 
    :math:`DN\_insolation` is the direct-normal insolation in one day 
    (kWh/m2/d)
    :math:`Ex\_insolation` is the the extraterestrial insolation in one 
    day (kWh/m2/d).  Computed using pvlib.irradiance.extraradiation.
    
    Parameters
    -----------
    dni : Pandas DataFrame
        Direct normal irradiance
        
    tfilter : Pandas Series (default = None)
        Time filter containing boolean values for each time index
        
    per_day : Boolean (default = True)
        Flag indicating if the results shoudl be computed per day
        
    Returns
    -------
    Kt : Pandas DataFrame or float
        Clearness index, if per_day = True, then a dataframe indexed by day is 
        returned, otherwise a single vlaue is returned for the entire dataset.
    """
    try:
        import pvlib
    except:
        logger.info('Could not import pvlib')
        return
        
    logger.info("Compute Clearness Index")
    
    df = dni
    
    trans = {'dni': dni.columns}
    
    # Remove time filter
    if tfilter is not None:
        df = df[tfilter]
    
    if per_day:
        dates = [df.index[0].date() + datetime.timedelta(days=x) for x in range(0, (df.index[-1].date()-df.index[0].date()).days+1)]

        Kt = pd.DataFrame(index=pd.to_datetime(dates))
        
        for date in dates:
            df_date = df.loc[date.strftime('%m/%d/%Y')]
            try:
                Ea = pvlib.irradiance.extraradiation(df_date.index.dayofyear)
                Ea = pd.DataFrame(index=df_date.index, data=Ea)
                dni = df_date[trans['dni']] # W/m2
                Ea = Ea[~dni.isnull().any(axis=1)]
                dni = dni[~dni.isnull().any(axis=1)]
                dnInsolation = np.sum(dni, axis=0)
                EaInsolation = np.sum(Ea, axis=0)
                Kt.loc[date, 'Clearness Index'] = float(np.divide(dnInsolation, EaInsolation))
            except:
                Kt.loc[date, 'Clearness Index'] = 'NaN'
    else:
        Ea = pvlib.irradiance.extraradiation(df.index.dayofyear)
        Ea = pd.DataFrame(index=df.index, data=Ea)
        dni = df[trans['dni']] # W/m2
        Ea = Ea[~dni.isnull().any(axis=1)]
        dni = dni[~dni.isnull().any(axis=1)]
        dnInsolation = np.sum(dni, axis=0)
        EaInsolation = np.sum(Ea, axis=0)
        Kt = np.divide(dnInsolation, EaInsolation)
        
    return Kt
    