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

All the configuration is done in command line. Just call the script with no parameter and you will get the help.

Running
------------------

On linux and Mac just 

```bash
./HTTP_server.py -s http://localhost:9091 -r /rest/
```

On windows
```bash
python HTTP_server.py -s http://localhost:9091 -r /rest/
```


Improvement & Bug fix
=============

* Header were not sent and not sent back
* code improvment to log more efficiently
* command line parmeter management
* TODO : Manage different source folder than the where the script is running