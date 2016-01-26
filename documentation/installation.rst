Installation
======================================

Pecos can be installed as a python package using pip or from source using git.  

To install using pip (**NOT COMPLETE**)::

	pip install pecos 
	
To build from source using git (**NOT COMPLETE**)::

	git clone https://github.com/pecos 
	cd pecos
	python setup.py install

Pecos is a python package which requires Python 2.7 along with several python 
package dependencies, including:

* Pandas: analyze and store time series data, 
  http://pandas.pydata.org/
* Numpy: support large, multi-dimensional arrays and matrices, 
  http://www.numpy.org/
* Matplotlib: produce figures, 
  http://matplotlib.org/

The following python packages are optional:

* pyyaml: store configuration options in human readable data format,
  http://pyyaml.org/
* win32com: send email

All other dependencies are part of the Python Standard Library.

To use Pecos, import the package from within a python console::

	import pecos	