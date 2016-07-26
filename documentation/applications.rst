Custom applications
====================

Pecos can be customized for specific applications.  Python scripts can be added 
to initialize data and add application specific models.  Additional quality control tests 
can be added by inheriting from the PerformanceMonitoring class.

PV system monitoring
---------------------
For PV systems, the translation dictionary can be used to group data
according to the system architecture, which can include multiple strings and modules.
The time filter can be defined based on sun position and system location.
The data objects used in Pecos are compatible with PVLIB, which can be used to model PV 
systems [Stein2016]_ (http://pvlib-python.readthedocs.io/).
Pecos also includes a function to read Campbell Scientific ascii file format and 
functions to compute pv performance metrics (i.e. performance ratio, clearness index).

Pecos includes a PV system example, **pv_example.py**, in the examples/pv directory.  
The example uses graphics functions in **pv_graphics.py**.

Performance metrics
---------------------
The performance metrics file, created by Pecos, can be used in additional 
analysis to track system health over time.

Pecos includes a performance metrics example (based on PV metrics), **metrics_example.py**, in the examples/metrics directory.

