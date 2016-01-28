Task scheduler 
===============

To run Pecos on an automated schedule, create a task using your operating systems
task scheduler.  On Windows, open the Control Panel and search for *Schedule Tasks*.
The task can be set to run at a specified time and the action can be set to run a
batch file (.bat or .cmd file name extension), which calls a python driver script.  
For example, the following batch file runs driver.py::

	cd your_working_directory
	C:\Python27\python.exe driver.py
