Performance metrics
==========================

Pecos can be used to track performance of time series data over time.  
The quality control index (QCI) is a general metric which indicates the 
percent of the data points that passed quality control tests.  
Duplicate and non-monotonic indexes are not counted as failed tests 
(duplicates are removed and non-monotonic indexes are reordered).  
QCI is defined as:

.. math::
	QCI = \frac{\sum_{d \in D}\sum_{t \in T} X_{dt}}{|DT|}
	
where 
:math:`D` is the set of data columns and 
:math:`T` is the set of timestamps in the analysis.  
:math:`X_{dt}` is a data point for column :math:`d` time t` that passed all quality control test.  
:math:`|DT|` is the number of data points in the analysis.

A value of 1 indicates that all data passed all tests.  
For example, if the data consists of  10 columns and 720 times that are 
used in the analysis, then :math:`|DT|` = 7200.  If 7000 data points pass all 
quality control tests, then the QCI is 0.972.

To compute QCI::

	QCI = pecos.metrics.qci(pm)

Additional metrics can be added to the QCI DataFrame and saved to a file::

	pecos.io.write_metrics(metrics_filename, QCI)

If 'metrics_filename' already exists, the metrics will be appended to the file.
