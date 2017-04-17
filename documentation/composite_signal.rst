Composite signals
==================

Composite signals are new data signal generated from existing data or from models.  
Composite signals can be used to add modeled data values or relationships between 
data columns to quality control tests.  

In the :ref:`simple_example`, a 'Wave Model' composite signal is added to the PerformanceMonitoring object::

	elapsed_time= pm.get_elapsed_time()
	wave_model = np.sin(10*(elapsed_time/86400))
	wave_model.columns=['Wave Model']
	pm.add_signal('Wave Model', wave_model)
