Performance Monitoring using Pecos
================================================================

Advances in sensor technology have rapidly increased our ability to monitor 
natural and human-made physical systems.  
In many cases, it is critical to process the resulting large volumes of data on a regular schedule
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
To cite Pecos, use one of the following references:

* K.A. Klise and J.S. Stein (2016), Performance Monitoring using Pecos, Technical Report SAND2016-3583, Sandia National Laboratories. :download:`pdf <pdfs/Pecos_ReportV0.1_SAND2016-3583.pdf>`
* K.A. Klise and J.S. Stein (2016), Automated Performance Monitoring for PV Systems using Pecos, 43rd IEEE Photovoltaic Specialists Conference (PVSC), Portland, OR, June 5-10. `pdf <http://www.pvsc-proceedings.org./download.php?year=2016&file=907>`_

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
   whatsnew
   developers
   API documentation <apidoc/pecos>
   reference

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


