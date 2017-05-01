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
The current version of this function uses the read_register() and read_registers() 
functions from minimalmodbus (https://minimalmodbus.readthedocs.io/en/master/).  

The read_register function:

	16 bit registers
	
	interger values between 0 to 65535("Unsigned INT16")
	
	integer values between -32768 to 32767("Signed INT16")
	
The read_registers function:

	16 bit registers
	
	interger values between 0 to 65535("Unsigned INT16") 

The function cycles through the pre-defined devices and channels.  It automatically 
uses the read_register or read_registers minimalmodbus functions depending on the 
configuration file settings. 

Scale value(s)
-----------------------------
The modbus values are stored in a string and scaled using 

	Scaled Values = [a*b for a,b in zip(Scale Factors,Values)]


Output: Stored Sensor Values (MySQL)
-----------------------------
The scaled values are converted into a pandas DataFrame and inserted into a MySQL database
using the sqlalchemy engine

	from sqlalchemy import create_engine

	engine = create_engine('mysql://'+user+':'+pswd+'@'+host+'/'+db)
		
	df.to_sql(name='%s'%table,con=engine, if_exists='append', index=False)

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
Each device has a specific connection requiremsnets.  This includes the usb port, address,
baud rate, parity, byte_size, stopbits, and timeout.  The configuration file also defines
if there are consecutive channels and/or single channels to be read.  The consecutive channels 
use the read_registers() function and the single channels use the read_register().

The scale factors for each device are also defined as a single string in the configuration 
file.  The sensor type and name are each describe as a string.
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








