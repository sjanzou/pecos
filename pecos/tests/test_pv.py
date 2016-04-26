from nose.tools import *
from os.path import abspath, dirname, join
import pandas as pd
import ephem
import pvlib
import numpy as np
import datetime
import pecos

testdir = dirname(abspath(__file__))
datadir = join(testdir,'data')

def test_sun_position_pvlib():

    # Albuquerque
    # Sunrise on 12/10/2015 = 7:04, 118 degrees
    # Subset on 12/10/2015 = 4:55, 242 degrees
    
    timeseries = pd.DatetimeIndex(pd.date_range('12/10/2015', periods=24*60, freq='Min'))
    timeseries = timeseries.tz_localize('MST')
    
    # pvlib python
    Location = pvlib.location.Location
    Location.latitude = 35.04;
    Location.longitude = -106.62;
    #Location.altitude = 1619;
    #Location.tz = 'US/Mountain'
    
    sun_position = pvlib.solarposition.ephemeris(timeseries, Location.latitude, Location.longitude);
    sun_position.index = sun_position.index.tz_localize(tz=None)
    
    #sun_position.plot()
    
    sunrise_el = sun_position.loc['2015-12-10 7:04:00', 'apparent_elevation']
    expected = 0
    assert_less(abs(sunrise_el-expected), 0.5) # 0.5 degree
    
    sunset_el = sun_position.loc['2015-12-10 16:55:00', 'apparent_elevation']
    expected = 0
    assert_less(abs(sunset_el-expected), 0.5) # 0.5 degree
    
    sunrise_az = sun_position.loc['2015-12-10 7:04:00', 'azimuth']
    expected = 118
    assert_less(abs(sunrise_az-expected), 0.5) # 0.5 degree
    
    sunset_az = sun_position.loc['2015-12-10 16:55:00', 'azimuth']
    expected = 242
    assert_less(abs(sunset_az-expected), 0.5) # 0.5 degree

    return sun_position

def test_sun_position_ephem():
    
    # Albuquerque
    # Sunrise on 12/10/2015 = 7:04, 118 degrees
    # Subset on 12/10/2015 = 4:55, 242 degrees
    
    timeseries = pd.DatetimeIndex(pd.date_range('12/10/2015', periods=24*60, freq='Min'))
    
    sun = ephem.Sun()
    o = ephem.Observer()
    o.lat = '35.04'
    o.long = '-106.62'
    o.elev = 1619 
    o.horizon = '-0:34'
    utc_offset = -7
        
    sun_position = pd.DataFrame(columns=['azimuth', 'elevation'], index = timeseries)
    
    for date in timeseries:
        local_date = ephem.Date(datetime.datetime(year=date.year, month=date.month, \
            day=date.day, hour=date.hour, minute = date.minute, second = date.second))
        UTCdate = ephem.Date(local_date - utc_offset*ephem.hour)
        o.date = UTCdate
        sun.compute(o)
        sun_position.loc[date, 'azimuth'] = sun.az * 180/np.pi # convert to degrees,  0 = North to 270 = West (east of north)
        sun_position.loc[date, 'elevation'] = sun.alt * 180/np.pi
    
    sun_position = sun_position.convert_objects(convert_numeric=True)
    
    #sun_position.plot()
    
    sunrise_el = sun_position.loc['2015-12-10 7:04:00', 'elevation']
    expected = 0
    assert_less(abs(sunrise_el-expected), 0.5) # 0.5 degree
    
    sunset_el = sun_position.loc['2015-12-10 16:55:00', 'elevation']
    expected = 0
    assert_less(abs(sunset_el-expected), 0.5) # 0.5 degree
    
    sunrise_az = sun_position.loc['2015-12-10 7:04:00', 'azimuth']
    expected = 118
    assert_less(abs(sunrise_az-expected), 0.5) # 0.5 degree
    
    sunset_az = sun_position.loc['2015-12-10 16:55:00', 'azimuth']
    expected = 242
    assert_less(abs(sunset_az-expected), 0.5) # 0.5 degree

    return sun_position
    