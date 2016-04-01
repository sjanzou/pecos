Time filter
=============

A time filter is a Boolean time series that indicates if specific timestamps should be
used in quality control tests.  The time filter can be defined using
elapsed time, clock time, or other custom algorithms. 
Pecos includes methods to get the elapsed and clock time of the DataFrame (in seconds).

The following example defines a time filter between 3 AM and 9 PM::

	clock_time = pm.get_clock_time()
	time_filter = (clock_time > 3*3600) & (clock_time < 21*3600)
	
The time filter can also be defined based on sun position, see **pv_example.py** in the examples/pv directory.

The time filter can then be added to the PerformanceMonitoring object as follows::

	pm.add_time_filter(time_filter)


