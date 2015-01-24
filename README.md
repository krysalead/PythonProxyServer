Python HTTP and Proxy
===========

This script allow to start a server that will serve the static content from a sub directory of where it was launch and forward all other request to an application server. This is useful when you want to work on mobile application targeting cordova (hybrid environement) but debugging in a browser so you can't do cross domain call.

How to use it
=============

Installation
------------------

Check that you have python 2.6.* installed on your computer and available in command line.
Just copy the HTTP_server.py into the folder you have your static files.

Configuration
------------------

Open the script with your favorit editor and modify those parameters:

* APPLICATION_SERVER = 'http://localhost:9091'
* ROUTING_KEY_WORD = '/rest'

**APPLICATION_SERVER** represent the entry point of the service you want to target
**ROUTING_KEY_WORD** is the keyword in the URL that indicate to the script to forward to the application server

Running
------------------

On linux and Mac just 

```bash
./HTTP_server.py
```

On windows
```bash
python HTTP_server.py
```


Improvement
=============

* Manage multiple entry point and multiple filter
