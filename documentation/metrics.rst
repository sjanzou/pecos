Performance metrics
==========================

Pecos can be used to track a wide range of performance metrics.
In general, a performance metric is any calculation that aggregates over time.
Performance metrics can be saved to track long term system health using the 
:class:`~pecos.io.write_metrics` method, as shown in :ref:`results`.

Quality control index
-------------------------
The quality control index (QCI) is a general metric which indicates the 
percent of data points that pass quality control tests.  
Duplicate and non-monotonic indexes are not counted as failed tests 
(duplicates are removed and non-monotonic indexes are reordered).  
A value of 1 indicates that all data passed all tests.  
For example, if the data consists of 10 columns and 720 times and 
7000 data points pass all quality control tests, then the QCI is (7000/(10*720)) = 0.972.
QCI is computed using the :class:`~pecos.metrics.qci` method.

To compute QCI,

.. doctest::
    :hide:

    >>> import pandas as pd
    >>> import numpy as np
    >>> import pecos
    >>> pm = pecos.monitoring.PerformanceMonitoring()
    >>> index = pd.date_range('1/1/2017', periods=24, freq='H')
    >>> data = {'A': np.arange(24)}
    >>> df = pd.DataFrame(data, index=index)
    >>> pm.add_dataframe(df)
	
.. doctest::

    >>> mask = pm.get_test_results_mask()
    >>> QCI = pecos.metrics.qci(mask)

Root mean square error
-------------------------

The root mean squared error (RMSE) is used to compare the 
difference between two variables.  
RMSE is often used to compare measured to modeled data.
RMSE is computed using the :class:`~pecos.metrics.rmse` method.
	
Time integral
-------------------------

A time integral is used to integrate over time-series data.
For example, time integrals can be used to compute energy from power, or insolation from irradiance.
A time integral is computed using the :class:`~pecos.metrics.time_integral` method.

Probability of detection and false alarm rate 
-------------------------------------------------

The probability of detection (PD) and false alarm rate (FAR) are used to
evaluate how well a quality control test (or set of quality control tests) distinguishes background from anomalous conditions.
PD and FAR are related to the number of true negatives, false negatives, false positives, and true positives, as shown in :numref:`fig-FAR-PD`.
The estimated condition is computed using results from quality control tests in Pecos, the actual condition must be supplied by the user.
If actual conditions are not known, anomalous conditions can be superimposed in the raw data to generate a testing data set.
A "good" quality control test (or tests) result in a PD close to 1 and FAR close to 0.

Receiver Operating Characteristic (ROC) curves are used to compare the effectiveness of different quality control tests, as shown in :numref:`fig-ROC`.
To generate a ROC curve, quality control test input parameters (i.e. upper bound for a range test) are systematically adjusted.
PD and FAR are computed using the :class:`~pecos.metrics.probability_of_detection` and :class:`~pecos.metrics.false_alarm_rate` methods.

.. _fig-FAR-PD:
.. figure:: figures/PD-FAR.png
   :scale: 55 %
   :alt: FAR and PD
   
   Relationship between FAR and PD.
 
.. _fig-ROC:
.. figure:: figures/ROC.png
   :scale: 50 %
   :alt: ROC
   
   Example ROC curve.

