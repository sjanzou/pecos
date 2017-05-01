Device to Client
==================

The :class:`~pecos.io.device_to_client` function collects data from a modbus device and stores it in a local 
database.  

Input
----------------------------- 
The function requires two inputs:
* Configuration File
* Log file directory
 

Read Channel(s) on modbus device
-----------------------------


Scale value(s)
-----------------------------



Output: Stored Sensor Values (MySQL or CSV)
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


**Channel Information**  

.. code-block:: json
	"DeviceA": [
        {
        	"Connection":[
            	{
            		"usb": "/dev/ttyUSB0",
            		"address":21,
            		"consecutive_channels":"True",
            		"single_channels":"True",
            		"baud":9600,
            		"parity": "N",
            		"byte_size":8,
            		"stopbits":1,
            		"timeout":0.05,
            		"fcode":4
            	}
            ],
            
            "consecutive_channels":[0,1,2,3,4,5,6,7],
            "single_channels":[128],
            "single_channels_signed":[true],

            "Scale":[0.1,0.1,0.1,0.1,0.1,0.01,0.0,0.0,0.01],
            
            "Type":[
            	"Temp",
            	"Temp",
            	"Temp",
            	"Temp",
            	"Temp",
            	"Humidity",
            	"Empty",
            	"Empty",
            	"Temp"
            ],
            
            "Name":[
            	"Spire_Ambient",
            	"Spire_NE",
            	"Spire_SW",
            	"Thermostat",
            	"Humid_Temp",
            	"Humidity",
            	"Temp_Ch6",
            	"Temp_Ch7",
            	"MLTL_CJC"
            ]
        }       
    ]








