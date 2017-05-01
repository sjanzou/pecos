Device to Client
==================

The :class:`~pecos.io.device_to_client` function collects data from a modbus device and stores it in a local 
database.     

Input: Configuration File 
-----------------------------

The configuration file is structured as follows:

.. code-block:: json

    {
        "DAQ": [
        	{
        	
        	}
        ],
        "Device A": [
        	{
        	
        	}
        ]
    }


**DAQ Information**

* Device Names
* Data Storage Credential (MySQL)
	- 1
* Collection Interval



**Data Storage Credentials**

* IP Address (ip)
* Port (port)
* Database (db)
* Table (table)
* Username (user)
* Password (pswd)

**Device Information**

* Connection
* Scale Factors
* Sensor Type
* Sensor Name


Read Channel(s) on modbus device
-----------------------------


Scale value(s)
-----------------------------



Output: Stored Sensor Values (MySQL or CSV)
-----------------------------