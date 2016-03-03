Translation dictionary
-----------------------
A translation dictionary maps database column names into common names.  
By default, Pecos assumes the translation is 1:1 (i.e. raw column names are used).

The translation dictionary can also be used to group columns with similar 
properties into a single variable.  
Each entry is a key:value pair where 'value' is a list of column names in the database.  
For example, {temp: [temp1,temp2]} means that columns named 'temp1' and 'temp2'  in the 
database file are assigned to the key 'temp' in Pecos, for example::
 
	trans = {
	  Linear: [A],
	  Random: [B],
	  Wave: [C,D]}

The translation dictionary can then be added to the PerformanceMonitoring object as follows::

	pm.add_translation_dictonary(trans, system_name)

As with DataFrames, multiple translation dictionaries can be added to the 
PerformanceMonitoring object, distinguished by the 'system_name'.

Keys defined in the translation dictionary can be used in quality control tests,
for example::

	pm.check_range([-1,1], 'Wave')

Inside Pecos, the translation dictonary is used to index into the DataFrame, for example::

	pm.df[pm.trans['Wave']]

returns columns C and D from the DataFrame.

