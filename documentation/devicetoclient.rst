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
        		"Device Names, Database Credentials, Collection Information"
        	}
        ],
        "Device A, ..., N": [
        	{
        	
        	}
        ]
    }


**DAQ (Data Acquisition)**

.. code-block:: json

    {
        "DAQ": [
        	{
        		"Devices":[
    			"ICPDAS1"
    			],
    		"Database":[
    			{
    				"ip": "127.0.0.1",
    				"port":3306,
    				"db":"solar",
    				"table":"predicts",
    				"user":"pseldata",
    				"pswd":"sanddb"
    			}
    		],
    		"Collection":[{
    			"Interval":1,
    			"Retries":5
    			}
    		]
        	
        	}
        ]
    }

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