Developers
==========

The development team includes:

* Katherine Klise, kaklise@sandia.gov
* Joshua Stein, jsstein@sandia.gov

To cite Pecos, use the following references:

* K.A. Klise and J.S. Stein (2016), Performance Monitoring using Pecos, Documentation and Use Cases. Technical Report SAND2016-XXXX, Sandia National Laboratories. (PDF version of this website).

* K.A. Klise and J.S. Stein (2016), Automated Performance Monitoring for PV Systems using Pecos, 43rd IEEE Photovoltaic Specialists Conference, Portland, OR, June 5-10

Testing
-------

Pecos includes automated tests run on (TravisCI??) the Jenkins continuous build and test server at Sandia National Laboratories.
Tests can be run locally using nosetests::

	nosetests -v --with-coverage --cover-package=pecos pecos

