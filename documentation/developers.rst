Developers
==========

The development team includes:

* Katherine Klise, kaklise@sandia.gov
* Joshua Stein, jsstein@sandia.gov

To cite Pecos, use the following reference:

* K.A. Klise and J.S. Stein (2016), Performance Monitoring using Pecos, Documentation and Use Cases. Technical Report SAND2016-XXXX, Sandia National Laboratories. (PDF version of this website).


Testing
-------

Pecos includes automated tests run on the Jenkins continuous build and test server at Sandia National Laboratories.
Tests can be run locally using nosetests::

	nosetests -v --with-coverage --cover-package=pecos pecos

