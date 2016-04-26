Time series data
==================

Pandas DataFrames store 2D data with labeled columns.  Pecos uses Pandas DataFrames
to store and analyze data indexed by time.  Pandas includes a wide range of 
time series analysis and date-time functionality.
To import pandas::

	import pandas as pd

Pandas includes many built-in functions to read data from csv, excel, sql, etc.
For example, data can be loaded from an excel file using::

	df = pd.read_excel('data.xlsx')

The :doc:`PerformanceMonitoring</apidoc/pecos.PerformanceMonitoring>` class is 
the base class used by Pecos to define performance monitoring analysis. 
To get started, an instance of the PerformanceMonitoring class is created::

	pm = pecos.monitoring.PerformanceMonitoring()

The DataFrame can then be added to the PerformanceMonitoring object as follows::
	
	pm.add_dataframe(df, system_name)

Multiple DataFrames can be added to the PerformanceMonitoring object.  
The 'system_name' is used to distinguish DataFrames.

DataFrames are accessed using::

	pm.df

