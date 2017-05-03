Data acquisition
==================

Pecos includes basic data acquisition methods to transfer data from sensors to an SQL database.  
These methods require the Python packages 
sqlalchemy (https://www.sqlalchemy.org/) and 
minimalmodbus (https://minimalmodbus.readthedocs.io). 

.. _devicetoclient_config:

Device to client
-------------------

The :class:`~pecos.io.device_to_client` method collects data from a modbus device and stores it in a local 
MySQL database. 
The method requires several configuration options, which are stored as a nested dictionary.
pyyaml can be used to store configuration options in a file.
The options are stored in a **Client** block and a **Devices** block.  
The Devices block can define multiple devices and each device can have multiple data streams.
The configuration options are described below.

* **Client**: A dictionary that contains information about the client.  
  The dictionary has the following keys:

  * **IP**: IP address (string) 
  * **Database**: name of database (string) 
  * **Table**: name of table (string)
  * **Username**: name of user (string)
  * **Password**: password for user (string)
  * **Interval**: data collection frequency in seconds (integer)
  * **Retries**: number of retries for each channel (integer)

* **Devices**: A list of dictionaries that contain information about each device (one dictionary per device).  
  Each dictionary has the following keys:

  * **Name**: modbus device name (string)
  * **USB**: serial connection (string) e.g. /dev/ttyUSB0 for linux
  * **Address**: modbus slave address (string)       
  * **Baud**: data transfer rate in bits per second (integer)
  * **Parity**: set parity of transmitted data for error checking (string) Possible values: N, E, O
  * **Bytes**: number of data bits (integer)
  * **Stopbits**: number of stop bits (integer)
  * **Timeout**: read timeout value in seconds (integer)  
  * **Data**: A list of dictionaries that contain information about each data stream (one dictionary per data stream). 
    Each dictionary has the following keys:
  
    * **Name**: Data name (string)
    * **Type**: Data type (string)
    * **Scale**: Scaling factor (integer)
    * **Conversion**: Conversion factor (float)
    * **Channel**: Register number (integer)
    * **Signed**: define if the data should be interpreted as unsigned or signed.  Can be True or False (bool)
    * **Fcode**: modbus function code.  Can be 3 or 4 (integer) 

Example configuration options are shown below.

.. literalinclude:: ../pecos/templates/device_to_client.yml
