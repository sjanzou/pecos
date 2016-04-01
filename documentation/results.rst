Results
==========

When a test fails, information is stored in::

	pm.test_results

Test results includes the following information:

* System Name: System name associated with the data file

* Variable Name: Column name in the data file

* Start Date: Start time of the failure

* End Date: : End time of the failure

* Timesteps: The number of consecutive timesteps involved in the failure

* Error Flag: Error messages include:

  * Duplicate timestamp
 
  * Nonmonotonic timestamp
 
  * Missing data (used for missing data and missing timestamp)
 
  * Corrupt data
 
  * Data > upper bound, value
 
  * Data < lower bound, value
 
  * Increment > upper bound, value
 
  * Increment < lower bound, value

Pecos can be used to generate an HTML report, test results CSV file, and a performance metrics CSV File.

Monitoring report
-------------------------------
The monitoring report include the start and end time for analysis, custom graphics 
and performance metrics, a table that includes test results, graphics associated 
with the test results (highlighting data points that failed a quality control tests), 
notes on runtime errors and warnings, and (optionally) the configuration options 
used in the analysis.

* **Custom Graphics:**
  Custom graphics can be created for a specific applications.  These graphics 
  are included at the top of the report.
  Any graphic with the name *custom* in the subdirectory are included in the 
  custom graphics section.  By default, no custom graphics are generated.

* **Performance Metrics:**
  Performance metrics are displayed in a table.

* **Test Results**
  Test results contain information stored in pm.test_results
  Graphics follow that display the data point(s) that caused the failure.  

* **Notes:**
  Notes include Pecos runtime errors and warnings.  Notes include:
  
  * Empty/missing database
  * Formatting error in the translation dictionary
  * Insufficient data for a specific quality control test
  * Insufficient data or error when evaluating string

* **Configuration Options:**
  Optional.  Configuration options used in the analysis.

The following method can be used to write a monitoring report::

	pecos.io.write_monitoring_report()

Test results
----------------------
The test results CSV file contains information stored in pm.test_results.

The following method can be used to write test results::

	pecos.io.write_test_results()
	
Performance metrics
-----------------------------
The performance metrics CSV file contains metrics.  
Values are appended each time an analysis is run.  

The following method can be used to write metrics to a file::

	pecos.io.write_metrics()
	
Dashboard
-----------
To compare performance of several systems, key graphics and metrics
can be gathered in a dashboard view.  
For example, the dashboard can contain multiple rows (one for each system) and multiple columns (one for each location).  
The dashboard can be linked to specific monitoring reports for more detailed information.

For each row and column in the dashboard, the following information can be specified

* Text (i.e. general information about the system/location)

* Graphics (i.e. a list of custom graphics)

* Table (i.e. a Pandas DataFrame with performance metrics)

* Link (i.e. the path to monitoring report for detailed information)

The following method can be used to write a monitoring report::

	pecos.io.write_dashboard()

Pecos includes a dashboard example, **dashboard_example.py**, in the examples/dashboard directory.
