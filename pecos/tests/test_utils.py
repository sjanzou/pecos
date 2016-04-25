from nose.tools import *
import pandas as pd
import pecos

index = pd.DatetimeIndex(['1/1/2016 00:00:14', 
                          '1/1/2016 00:00:30',
                          '1/1/2016 00:00:40',
                          '1/1/2016 00:00:44',
                          '1/1/2016 00:00:59',
                          '1/1/2016 00:01:00',
                          '1/1/2016 00:01:14',
                          '1/1/2016 00:01:32',
                          '1/1/2016 00:01:45',
                          '1/1/2016 00:02:05'])

def test_round_index_nearest():
    new_index = pecos.utils.round_index(index, 15, 'nearest')
    nearest_index = pd.DatetimeIndex([
                          '1/1/2016 00:00:15', 
                          '1/1/2016 00:00:30',
                          '1/1/2016 00:00:45',
                          '1/1/2016 00:00:45',
                          '1/1/2016 00:01:00',
                          '1/1/2016 00:01:00',
                          '1/1/2016 00:01:15',
                          '1/1/2016 00:01:30',
                          '1/1/2016 00:01:45',
                          '1/1/2016 00:02:00'])
    diff = new_index.difference(nearest_index)
    assert_equals(len(diff), 0)

def test_round_index_floor():
    new_index = pecos.utils.round_index(index, 15, 'floor')
    floor_index = pd.DatetimeIndex([
                          '1/1/2016 00:00:00', 
                          '1/1/2016 00:00:30',
                          '1/1/2016 00:00:30',
                          '1/1/2016 00:00:30',
                          '1/1/2016 00:00:45',
                          '1/1/2016 00:01:00',
                          '1/1/2016 00:01:00',
                          '1/1/2016 00:01:30',
                          '1/1/2016 00:01:45',
                          '1/1/2016 00:02:00'])
    diff = new_index.difference(floor_index)
    assert_equals(len(diff), 0)

def test_round_index_ceiling():
    new_index = pecos.utils.round_index(index, 15, 'ceiling')
    ceiling_index = pd.DatetimeIndex([
                          '1/1/2016 00:00:15', 
                          '1/1/2016 00:00:30',
                          '1/1/2016 00:00:45',
                          '1/1/2016 00:00:45',
                          '1/1/2016 00:01:00',
                          '1/1/2016 00:01:00',
                          '1/1/2016 00:01:15',
                          '1/1/2016 00:01:45',
                          '1/1/2016 00:01:45',
                          '1/1/2016 00:02:15'])
    diff = new_index.difference(ceiling_index)
    assert_equals(len(diff), 0)

def test_round_index_invalid():
    new_index = pecos.utils.round_index(index, 15, 'invalid')
    diff = new_index.difference(index)
    assert_equals(len(diff), 0)
