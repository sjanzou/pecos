Results
==========

When a test fails, information is stored in::

	pm.test_results

Test results includes the following information:

* System Name: System name associated with the data file

* Variable Name: Column name in the data file

* Start Date: Start time of the failure

* End Date: : End time of the failure

* Timesteps: The number of consecutive timestemps involved in the failure

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

HTML report
----------------------
The HTML report include the start and end time for analysis, custom graphics 
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
  Performance metrics added during analysis are displayed in a table.

* **Test Results**
  Test results contain infomation stored in pm.test_results
  Graphics follow that display the data point(s) that caused the failure.  

* **Notes:**
  Notes include Pecos runtime errors and warnings.  Notes include:
  
  * Empty/missing database
  * Formatting error in the translation dictionary
  * Insufficient data for a specific quality control test
  * Insufficient data or error when evaluating a composite equation

* **Configuration Options:**
  Optional.  Configuration options used in the analysis.
  
Test Results CSV File
----------------------
The test results CSV file contains informantion stored in pm.test_results.

Performance Metrics CSV File
-----------------------------
The performance metrics CSV file contains metrics added during analysis, values 
are appended each time an analysis is run.
