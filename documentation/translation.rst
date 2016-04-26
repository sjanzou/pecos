Translation dictionary
-----------------------
A translation dictionary maps database column names into common names.  
The translation dictionary can also be used to group columns with similar 
properties into a single variable.  

Each entry in a translation dictionary is a key:value pair where 
'key' is the common name of the data and 'value' is a list of original column names in the database.  
For example, {temp: [temp1,temp2]} means that columns named 'temp1' and 'temp2'  in the 
database file are assigned to the common name 'temp' in Pecos.
In the simple example, the following translation dictionary is used to rename column
'A' to 'Linear', 'B' to 'Random', and group columns 'C' and 'D' to 'Wave'::
 
	trans = {
	  Linear: [A],
	  Random: [B],
	  Wave: [C,D]}

The translation dictionary can then be added to the PerformanceMonitoring object as follows::

	pm.add_translation_dictionary(trans, system_name)

If no translation is desired (i.e. raw column names are used), a 1:1 map can be generated using the following code::

	trans = dict(zip(df.columns, [[col] for col in df.columns]))
	pm.add_translation_dictionary(trans, system_name)

As with DataFrames, multiple translation dictionaries can be added to the 
PerformanceMonitoring object, distinguished by the 'system_name'.

Keys defined in the translation dictionary can be used in quality control tests,
for example::

	pm.check_range([-1,1], 'Wave')

Inside Pecos, the translation dictionary is used to index into the DataFrame, for example::

	pm.df[pm.trans['Wave']]

returns columns C and D from the DataFrame.

