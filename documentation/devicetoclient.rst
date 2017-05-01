Device to Client
==================

The :class:`~pecos.io.device_to_client` function collects data from a modbus device and stores it in a local 
database.     

Capabilities 
-----------------------------


Process 
-----------------------------


Configuration File 
-----------------------------

The configuration file has two main sections that define the data acquisition and each 
individual devices as shown here:

.. code-block:: json

    {
        "DAQ": [
        	{
        		"Device Names, Database Credentials, and Collection Information"
        	}
        ],
        "Device 1, ..., N": [
        	{
        		"Modbus connection, channel information, scale factors, type, and names"
        	}
        ]
    }


**DAQ (Data Acquisition)**
The DAQ section of the configuration file defines the devices to be polled, the database 
that will store the data, and the collection interval and number of retries.  The number 
of devices can range from 1 to N.  The database credentials include the host ip address 
(127.0.0.1 or localhost for local storage),
MySQL port (typically 3306), database name, table name, username, and password.  The 
collection section defines the polling intervale (seconds) and the number of retries if a
connection error occurs. 

.. code-block:: json

    "DAQ": [
        	{
        		"Devices":[
    				"Device1",
    				"DeviceN"
    			],
    			"Database":[
    				{
    					"ip": "127.0.0.1",
    					"port":3306,
    					"db":"database name",
    					"table":"table name",
    					"user":"username",
    					"pswd":"password"
    				}
    			],
    			"Collection":[
    				{
    					"Interval":1,
    					"Retries":5
    				}
    			]
        	}
        ]



**Device Information**


**Connection**




Read Channel(s) on modbus device
-----------------------------


Scale value(s)
-----------------------------



Output: Stored Sensor Values (MySQL or CSV)
-----------------------------