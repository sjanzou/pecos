Performance Monitoring using Pecos
================================================================

Advances in sensor technology have rapidly increased our ability to monitor 
natural and human-made physical systems.  
The challenge is to turn the resulting large volumes of data into meaningful information. 
In many cases, it is critical to process this data on a regular schedule
and alert system operators when the system has changed.
Automated quality control and performance monitoring can allow system 
operators to quickly detect performance issues.  

Pecos is an open source python package designed to address this need.  
Pecos includes built-in functionality to monitor performance of time series data.  
The software can be used to automatically run a series of quality control 
tests and generate customized reports which include performance metrics, 
test results, and graphics.  The software was developed specifically for 
solar photovoltaic system monitoring, but it can be customized for other 
applications.

Citing Pecos
--------------
To cite Pecos, use the following reference:

* K.A. Klise and J.S. Stein (2016), Performance Monitoring using Pecos, Technical Report SAND2016-XXXX, Sandia National Laboratories.

Contents
------------
.. toctree::
   :maxdepth: 1
	
   overview
   installation
   example
   timeseries
   translation
   timefilter
   qc_tests
   metrics
   composite_signal
   configfile
   scheduler
   results
   applications
   license
   developers
   API documentation <apidoc/pecos>
   reference

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


