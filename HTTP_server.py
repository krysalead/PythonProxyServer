#!/usr/bin/python

"""
This server allow you to serve the static content from the folder of your choice below the root of the this script.
Then every request that contains a key word like "/rest" will be forwarded to another server (Application Server for instance)

Browser ---> Python HTTP server ---> Static content
                                \
                                  --> Application Server (localhost on different port)
"""

import SimpleHTTPServer
import SocketServer
import logging
import cgi

import urlparse
import urllib
import urllib2

import sys

APPLICATION_SERVER = 'http://localhost:9091'
ROUTING_KEY_WORD = '/rest'


if len(sys.argv) > 2:
    PORT = int(sys.argv[2])
    I = sys.argv[1]
elif len(sys.argv) > 1:
    PORT = int(sys.argv[1])
    I = ""
else:
    PORT = 8000
    I = ""


class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        global APPLICATION_SERVER
        logging.warning("======= GET Request =======")
        logging.warning(self.path)
        if self.path.startswith(ROUTING_KEY_WORD):
            url = APPLICATION_SERVER+self.path
            request = urllib2.Request(url, headers={"Accept" : "application/json"})
            request.add_header("Content-type", "application/json")
            response = urllib2.urlopen(request).read()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response)
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        
    def parse_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        logging.warning('Content Type:'+ctype);
        if ctype == 'multipart/form-data':
            logging.warning('multipart/form-data');
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            logging.warning('application/x-www-form-urlencoded');
            length = int(self.headers['content-length'])
            postvars = cgi.parse_qs(
                    self.rfile.read(length), 
                    keep_blank_values=1)
        elif ctype == 'application/json':
            length = int(self.headers['content-length'])
            postvars = cgi.parse_qs(
                    self.rfile.read(length), 
                    keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    def do_POST(self):
        global APPLICATION_SERVER
        logging.warning("======= POST Request =======")
        postvars = self.parse_POST()
        if self.path.startswith(ROUTING_KEY_WORD):
            url = APPLICATION_SERVER+self.path
            data = postvars.iterkeys().next();
            request = urllib2.Request(url, data)
            request.add_header("Content-type", "application/json")
            request.add_header("Accept", "application/json")
            #debug mode
            #request.set_proxy("127.0.0.1:8080","http")
            response = urllib2.urlopen(request).read()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response)
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_POST(self)

Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "Python http server version 0.1 (for testing purposes only)"
print "Serving at: http://%(interface)s:%(port)s" % dict(interface=I or "localhost", port=PORT)
httpd.serve_forever()
