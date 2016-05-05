Configuration file
==================

A configuration file can be used to store information about data and  
quality control tests.  The configuration file is not used directly within Pecos,
therefore there are no specific formatting requirements. 
Configuration files can be useful when using the same python script 
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
**Strings of python code should be thoroughly tested by the user.**  
A list of key:value pairs can be used to specify the order of evaluation.

When using a string of python code, keywords in {} are expanded using the following rules in this order:

1. Keywords ELAPSED_TIME and CLOCK_TIME return time in seconds

2. Keywords that are a key in the translation dictionary return 'pm.df[pm.trans[Keyword]]'

3. Keywords that are a key in a user specified dictionary of constants, specs, return 'specs[Keyword]'.
   
The values in specs can be used to 
generate a time filter, 
define upper and lower bounds in quality control tests, 
define system latitude and longitude, 
or other constants needed in composite equations, for example::
	
	specs = {
	  'Frequency': 900,  
	  'Multiplier': 10,
	  'Latitude': 35.054,  
	  'Longitude': -106.539}

Strings are evaluated and added to the DataFrame using the following code::

	signal = pm.evaluate_string(raw_column_name, string, specs)
	pm.add_signal(trans_column_name, signal)
	
If the string evaluation fails, the error message is printed in the final report.  

The script, **simple_example_using_config.py**, in the examples/simple directory uses a
configuration file and string evaluation.
