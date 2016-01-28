Composite signals
==================

Composite signals are used to generate new data columns based on existing data.  
Composite signals can be used to add modeled data values or relationships between 
data columns.  Data created from composite signals can be used in the quality 
control tests.  

The following example adds 'Wave Model' data to the PerformanceMonitor object::

	elapsed_time= pm.get_elapsed_time()
	wave_model = np.sin(10*(elapsed_time/86400))
	wave_model.columns=['Wave Model']
	pm.add_signal('Wave Model', wave_model)
