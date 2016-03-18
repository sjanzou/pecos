Configuration file
==================

A configuration file can be used to store information about data and  
quality control tests.  The configuration file is not used directly within Pecos,
therefore there are no specific formatting requirements. 
Configuration files can be useful when using the same driver script 
to analyze several systems that have slight differences.

The simple example includes a configuration file that defines 
system specifications, 
translation dictionary,
composite signals,
corrupt values,
and bounds for range and increment tests.

.. literalinclude:: ../examples/simple/simple_config.yml

In the configuration file, composite signals and time filters can be defined 
using strings of python code. 
Numpy (and other python modules if needed) can be used for computation.  
Code strings should be thoroughly tested.  
A list of key:value pairs can be used to specify the order of evaluation.

Keywords in {} are expanded using the following rules:

1. Keywords ELAPSED_TIME and CLOCK_TIME return time in seconds

2. Keywords that are a  key in the translation dictionary return 'pm.df[pm.trans[Keyword]]'

3. Keywords that are keys in a user specified dictionary of constants return 'specs[Keyword]'
	
If the composite signal fails, the error message is printed 
in the final report.  

The user specified dictionary, specs, contains system specific constants.  
For example, specifications could include the expected timestamp frequency.
These values can be used to check the timestamp, define upper and lower 
bounds in quality control tests, or as constants in composite equations::
	
	specs = {
	  'Frequency': 900,  
	  'Multiplier': 10,
	  'Latitude': 35.054,  
	  'Longitude': -106.539}
	  
