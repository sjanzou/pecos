Time series data
==================

Pandas DataFrames store 2D data with labeled columns.  Pecos uses Pandas DataFrames
to store and analyze data indexed by time.  Pandas includes a wide range of 
time series analysis and date-time functionality.  By using Pandas DataFrames, 
Pecos is able to take advantage of a wide range of timestamp strings, including
UTC offset. 

Pandas includes many built-in functions to read data from CSV, Excel, SQL, etc.
For example, data can be loaded from an excel file using the following code.

.. doctest::

    >>> import pandas as pd
    >>> df = pd.read_excel('data.xlsx') #doctest:+SKIP 

Data can also be gathered from the web using the Python package request, http://docs.python-requests.org.

The :class:`~pecos.monitoring.PerformanceMonitoring` class in Pecos is
the base class used to define performance monitoring analysis. 
To get started, an instance of the PerformanceMonitoring class is created.

.. doctest::

    >>> import pecos
    >>> pm = pecos.monitoring.PerformanceMonitoring()

A DataFrame can then be added to the PerformanceMonitoring object.

.. doctest::
    :hide:

    >>> df = pd.DataFrame()

.. doctest::

    >>> pm.add_dataframe(df)

Multiple DataFrames can be added to the PerformanceMonitoring object.  
DataFrames are merged using Pandas 'combine_first' method.

DataFrames are accessed using

.. doctest::

    >>> pm.df #doctest:+SKIP 

